source("src/Rscript/disk/disk_plot.R")
library(dplyr)
library(openxlsx)
library(ggplot2)
library(gmodels)

args <- commandArgs(trailingOnly = TRUE)
data_path <- args[1]
reference_path <- args[2]
output_path <- args[3]

# Create output directory if it does not exist
# if (!dir.exists(output_path)) {
#   dir.create(output_path, recursive = TRUE)
# }

get_data <- function(data_path, reference_path, output_path) {
  file <- data_path
  file2 <- reference_path

  Fasit_data <- read.xlsx(xlsxFile = file2)
  Lre_data <- read.xlsx(xlsxFile = file)

  names(Fasit_data) <- unname(Fasit_data[2, ])
  Fasit_data <- Fasit_data[-1, ]
  Fasit_data <- Fasit_data[-1, ]
  colnames(Fasit_data) <- c("Strain_no", "K_res", "EDL", "LIN_MIC_MTS", "LIN_MIC_Etest", "LIN_MIC_Etest_1")

  Lre_data$Species <- as.factor(Lre_data$Species)
  Lre_data$Strain_no <- as.factor(Lre_data$Strain_no)

  Disk_data <- Lre_data %>%
    select(Strain_no, Species, Disk_diff_Linezolid10, Disk_diffusion) %>%
    na.omit()

  disk_types <- unique(Disk_data$Disk_diffusion)
  disk_list <- setNames(vector("list", length(disk_types)), disk_types)

  process_data <- function(data, Fasit_data) {
    data$Strain_no <- as.factor(data$Strain_no)
    data$Species <- as.factor(data$Species)
    data$Strain_no <- droplevels(data$Strain_no)
    data$Species <- droplevels(data$Species)

    agg_data <- aggregate(Disk_diff_Linezolid10 ~ Strain_no, data = data, FUN = function(x) c(Mean = mean(x), SD = sd(x)))
    agg_data <- data.frame(Strain_no = agg_data$Strain_no, Mean = agg_data$Disk_diff_Linezolid10[, "Mean"], SD = agg_data$Disk_diff_Linezolid10[, "SD"])
    agg_data$Lower <- agg_data$Mean - 1.96 * agg_data$SD
    agg_data$Upper <- agg_data$Mean + 1.96 * agg_data$SD

    min_max_values <- tapply(data$Disk_diff_Linezolid10, data$Strain_no, FUN = function(x) c(Min = min(x, na.rm = TRUE), Max = max(x, na.rm = TRUE)))

    agg_data$max <- unlist(lapply(min_max_values, function(x) x["Max"]))
    agg_data$min <- unlist(lapply(min_max_values, function(x) x["Min"]))

    fasit_values <- Fasit_data[Fasit_data$Strain_no %in% unique(data$Strain_no), c("Strain_no", "K_res", "EDL")]
    fasit_values$Strain_no <- as.factor(fasit_values$Strain_no)
    data <- left_join(agg_data, fasit_values, by = "Strain_no")

    return(data)
  }

  # time = format(Sys.time(), "%Y%m%d%H%M%S")
  for (disk_type in disk_types) {
    processed_data <- Disk_data %>%
      filter(Disk_diffusion == disk_type) %>%
      mutate_at(vars(Disk_diff_Linezolid10), as.numeric) %>%
      process_data(., Fasit_data)

    disk_list[[disk_type]] <- processed_data

    draw_plot(processed_data, disk_type, output_path)
  }

  return(disk_list)
}

# Call get_data function
get_data(data_path, reference_path, output_path)
