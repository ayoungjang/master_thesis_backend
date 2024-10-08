library(survival)
library(dplyr)
library(fitdistrplus)
library(openxlsx)
library(ggplot2)
library(reshape2)
library(R2WinBUGS)
library(gmodels)
library(gdata)
library(statip)
library(jsonlite)
library(rjags)
source("src/Rscript/strip/strip_plot.R")

args <- commandArgs(trailingOnly = TRUE)
data_path <- args[1]
reference_path <- args[2]
output_path <- args[3]
anti_type <- "linezolid10"
output_path <- paste0(output_path, "/", anti_type)
# Create output directory if it does not exist
if (!dir.exists(output_path)) {
    dir.create(output_path, recursive = TRUE)
}


get_data <- function(data_path, reference_path, output_path) {
    file <- data_path
    file2 <- reference_path

    Fasit_data <- read.xlsx(xlsxFile = file2)
    Lre_data <- read.xlsx(xlsxFile = file)
    names(Fasit_data) <- unname(Fasit_data[2, ])

    Fasit_data <- Fasit_data[-1, ]
    Fasit_data <- Fasit_data[-1, ]
    colnames(Fasit_data) <- c("Strain_no", "LIN_mm_zone", "LIN_mm_zone_1", "LIN_MIC_MTS", "LIN_MIC_Etest", "LIN_MIC_Etest_1")

    Lre_data$Species <- as.factor(Lre_data$Species)
    Lre_data$Strain_no <- as.factor(Lre_data$Strain_no)

    Gradient_data <- Lre_data[, c("lab_id", "Strain_no", "Species", names(Lre_data)[grepl("Gradient", names(Lre_data))])]
    Gradient_data <- merge(Gradient_data, Fasit_data, by = "Strain_no", all.x = TRUE)

    Gradient_data <- na.omit(Gradient_data)
    Fasit_data <- na.omit(Fasit_data)

    Gradient_data <- within(Gradient_data, {
        MIC <- ifelse(grepl("E-test/bioMerieux", rownames(Gradient_data)), Fasit_data$`LIN_MIC_Etest`, Fasit_data$`LIN_MIC_MTS`)

        # event type: 3 = interval, 2 = left, 0 = right
        event <- rep(3, nrow(Gradient_data))
        event[union(grep("<", MIC), grep("<=", MIC))] <- 2
        event[union(grep(">", MIC), grep(">=", MIC))] <- 0
        # as numeric
        MIC.num <- as.numeric(sub("<", "", sub("<=", "", sub(">", "", sub(c(">="), "", ifelse(MIC == ">256", 512, MIC)))))) # nolint
        # log MIC
        log.MIC <- log2(MIC.num)
        # log MIC for naive mean
        log.MIC.naive <- ifelse(event != 0, log.MIC - 0.5, log.MIC + 0.5)
        # as Surv
        log.MIC.surv <- Surv(time = ifelse(event == 3, log.MIC - 1, log.MIC), time2 = log.MIC, event = event, type = "interval")
        # lower and upper for WinBUGS
        lower <- ifelse(event == 3, log.MIC - 1, ifelse(event == 2, -100, log.MIC))
        upper <- ifelse(event == 3, log.MIC, ifelse(event == 2, log.MIC, 100))
    })


    calculation <- function(data) {
        data$Strain_no <- as.factor(data$Strain_no)
        data$Species <- as.factor(data$Species)

        counts <- data %>%
            count(Strain_no) %>%
            rename(count = n) # Rename the count column to "count"

        # Continue with the rest of the function


        data$Strain_no <- drop.levels(data$Strain_no)
        data$Species <- drop.levels(data$Species)

        head(data$Species)

        # working dir


        wbwd <- file.path(getwd(), "src/Rscript/strip", "WinBUGS")


        # bugs model
        cat("model {
  #
  for (i in 1:n) {
    y[i] ~ dnorm(mu[i], tau) T(lower[i], upper[i])
    mu[i] <- inprod(X[i, ], beta[]) + b.lab[lab[i]]
  }

  for (j in 1:n.lab) {
    b.lab[j] ~ dnorm(0.0, tau.lab)
  }

  for (k in 1:n.beta) {
    beta[k] ~ dnorm(2.0, 6.0)
  }

  tau <- pow(sigma, -2)
  sigma ~ dunif(0.1, 2)
  tau.lab <- pow(sigma.lab, -2)
  sigma.lab ~ dunif(0.1, 2)
}", file = file.path(wbwd, "model.txt"))

        # bugs data
        X <- model.matrix(~ (Strain_no)^2, data = data)
        n <- nrow(X)
        n.beta <- ncol(X)

        data$lab_id <- as.factor(data$lab_id)
        n.lab <- nlevels(data$lab_id)


        jags.inits <- function() {
            list(
                y = with(data, runif(n, lower, upper)),
                b.lab = rnorm(n.lab, 0, 4), # 더 좁은 범위에서 초기값 설정
                beta = rnorm(n.beta, , 6), # 초기 beta 값도 좁은 범위에서 설정
                sigma = runif(1, 0.1, 2), # sigma 초기값을 0.1 ~ 2 사이로 설정
                sigma.lab = runif(1, 0.1, 2) # sigma.lab 초기값 설정
            )
        }


        jags.fit <- jags.model(
            file = file.path(wbwd, "model.txt"),
            data = list(
                n = n,
                lower = data$lower,
                upper = data$upper,
                X = X,
                n.beta = n.beta,
                n.lab = n.lab,
                lab = as.numeric(data$lab_id)
            ),
            inits = jags.inits,
            n.chains = 2,
            n.adapt = 100
        )

        update(jags.fit, n.iter = 100) # burn-in

        samples <- coda.samples(jags.fit, variable.names = c("beta", "b.lab", "sigma", "sigma.lab"), n.iter = 5000, thin = 10)
        b.lab <- as.matrix(samples)[, grep("b.lab", colnames(as.matrix(samples)))]
        beta <- as.matrix(samples)[, grep("beta", colnames(as.matrix(samples)))]


        # labs compared to mean
        lab.data <- data.frame(
            lab = levels(data$lab_id),
            diff.log.MIC = colMeans(b.lab),
            lower.diff.log.MIC = apply(b.lab, 2, quantile, 0.025),
            upper.diff.log.MIC = apply(b.lab, 2, quantile, 0.975)
        )


        data.newdata <- with(data, expand.grid(Strain_no = levels(Strain_no)))

        data.sub <- within(data.newdata, {
            lower.log.MIC.ref <- NA
            upper.log.MIC.ref <- NA
            ref.MIC <- NA
        })
        data.newdata <- within(data.newdata, {
            mode.log.MIC <- NA
            E.log.MIC.naive <- NA
            se.log.MIC.naive <- NA
        })

        k <- 1

        for (i in 1:nlevels(data$Strain_no)) {
            strain_value <- levels(data$Strain_no)[i]

            c_value <- subset(Fasit_data, Strain_no == strain_value) # correct answer (refmic data)

            data.data.sub <- subset(data, Strain_no == strain_value)

            mod <- with(data.data.sub, lm(log.MIC.naive ~ 1))

            frequency_values <- mfv(data.data.sub$MIC.num)

            # c_value$LIN_MIC_MTS <- as.numeric(sub("<", "", sub("<=", "" ,sub(">", "", sub(c(">="), "", c_value$LIN_MIC_MTS)))))
            c_value$LIN_MIC_MTS <- as.numeric(sub("<", "", sub("<=", "", sub(">", "", sub(c(">="), "", ifelse(c_value$LIN_MIC_MTS == ">256", 512, c_value$LIN_MIC_MTS))))))

            distances <- abs(frequency_values - c_value$LIN_MIC_MTS)

            nearest <- frequency_values[which.min(distances)]

            data.newdata[k, "mode.log.MIC"] <- log2(nearest)

            data.sub[k, "lower.log.MIC.ref"] <- log2(c_value$LIN_MIC_MTS) - 1
            data.sub[k, "upper.log.MIC.ref"] <- log2(c_value$LIN_MIC_MTS)
            # data.sub[k,"ref.MIC"]<- log2(c_value$LIN_MIC_Etest)

            data.newdata[k, c("E.log.MIC.naive", "se.log.MIC.naive")] <- c(coef(mod), sqrt(vcov(mod)))

            k <- k + 1
        }

        for (i in 1:nrow(data.newdata)) {
            strain_no <- data.newdata[i, "Strain_no"]

            # Find the matching species for the current Strain_no
            matching_species <- unique(data[data$Strain_no == strain_no, "Species"])

            # Combine the matching species into a single string
            combined_species <- paste(matching_species, collapse = ", ")

            # Add the combined species to data.newdata
            data.newdata[i, "Species"] <- combined_species
        }

        data.newdata <- within(data.newdata, {
            lower.log.MIC.naive <- E.log.MIC.naive - 1.96 * se.log.MIC.naive
            upper.log.MIC.naive <- E.log.MIC.naive + 1.96 * se.log.MIC.naive
        })

        X.samplepred <- model.matrix(~ (Strain_no)^2, data = data.newdata)
        mu_sample <- t(X.samplepred %*% t(beta))

        data.newdata <- within(data.newdata, {
            E.log.MIC <- colMeans(mu_sample)
            lower.log.MIC <- apply(mu_sample, 2, quantile, 0.025)
            upper.log.MIC <- apply(mu_sample, 2, quantile, 0.975)
        })

        data.newdata <- merge(data.newdata, data.sub, sort = FALSE)
        data.newdata$upper.log.MIC.ref <- as.double(data.newdata$upper.log.MIC.ref)
        data.newdata <- merge(data.newdata, counts, by = "Strain_no", all.x = TRUE)
        n <- ncol(X.samplepred)
        output <- list(data.newdata, n)
        return(output)
    }




    unique_types <- unique(Gradient_data$Gradient_test)
    results_list <- setNames(vector("list", length(unique_types)), unique_types)

    for (type in unique_types) {
        # counts <- data.frame()
        type_data <- Gradient_data[Gradient_data$Gradient_test == type, ]
        if (grepl("/", type)) {
            split_str <- strsplit(type, "/")[[1]][1]
        } else {
            split_str <- type
        }
        if (split_str == "Liofilchem") split_str <- "MTS"
        results_list[split_str] <- calculation(type_data)

        if (!dir.exists(output_path)) {
            dir.create(output_path, recursive = TRUE)
        }

        chg_data <- do.call(rbind.data.frame, results_list[split_str])
        chg_data <- chg_data[order(chg_data$Strain_no), ]
        json_file_path <- file.path(output_path, paste0(split_str, ".json"))
        write_json(chg_data, path = json_file_path, pretty = TRUE)

        # draw_plot(results_list[[type]], split_str, output_path)
    }
}

get_data(data_path, reference_path, output_path)
