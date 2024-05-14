library(dplyr)
library(openxlsx)
library(ggplot2)
library(gmodels)

DIR <- "/home/ayoung/Desktop/server/"
get_dir <-"/home/ayoung/Desktop/server/excels/"

file <- paste0(get_dir,"data.xlsx")
file2 <- paste0(get_dir,"reference.xlsx")



Fasit_data<-read.xlsx(xlsxFile=file2)
Lre_data <- read.xlsx(xlsxFile=file)

Distribution <- FALSE #Flag for distribution figure

names(Fasit_data) <- unname(Fasit_data[2, ])

Fasit_data <- Fasit_data[-1,]
Fasit_data <- Fasit_data[-1,]
colnames(Fasit_data) <- c("Strain_no", "K_res", "EDL","LIN_MIC_MTS","LIN_MIC_Etest","LIN_MIC_Etest_1")

Lre_data$Species <- as.factor(Lre_data$Species)
Lre_data$Strain_no <- as.factor(Lre_data$Strain_no)

Disk_data <-  Lre_data[,c("Strain_no","Species","Disk_diff_Linezolid10","Disk_diffusion")]

Disk_data <- na.omit(Disk_data)
Fasit_data <- na.omit(Fasit_data)

Disk_BD<- data.frame()
Disk_Oxoid <- data.frame()
Disk_Mast <- data.frame()

Disk_BD <- Disk_data[Disk_data$Disk_diffusion == "BD", ]
Disk_Oxoid <- Disk_data[Disk_data$Disk_diffusion == "Oxoid", ]
Disk_Mast <- Disk_data[Disk_data$Disk_diffusion == "Mast", ]
Disk_Rosco <- Disk_data[Disk_data$Disk_diffusion == "Rosco", ]

Disk_BD<- data.frame(Disk_BD[1],sapply(Disk_BD[2:3], function(x) as.numeric(as.character(x))),Disk_BD[4])
Disk_Oxoid<- data.frame(Disk_Oxoid[1],sapply(Disk_Oxoid[2:3], function(x) as.numeric(as.character(x))),Disk_Oxoid[4])
Disk_Mast<- data.frame(Disk_Mast[1],sapply(Disk_Mast[2:3], function(x) as.numeric(as.character(x))),Disk_Mast[4])

Disk_Oxoid$Strain_no <- as.numeric(Disk_Oxoid$Strain_no);
Disk_Oxoid <- Disk_Oxoid[order(Disk_Oxoid$Strain_no), ]

if(Distribution){
  source(paste0(DIR,"Rscript/disk/histogram.R"))
  draw_distribution_plot(Disk_Oxoid,Disk_BD,Disk_Mast)
  
}


process_data <- function(data) {
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

Disk_BD <- process_data(Disk_BD)
Disk_Oxoid <- process_data(Disk_Oxoid)
Disk_Mast <- process_data(Disk_Mast)
Disk_Rosco <- process_data(Disk_Rosco)

Disk_BD <- na.omit(Disk_BD)
Disk_Oxoid <- na.omit(Disk_Oxoid)
Disk_Mast <- na.omit(Disk_Mast)
Disk_Rosco <- na.omit(Disk_Rosco)

source(paste0(DIR,"Rscript/disk/disk_plot.R"))
draw_combine_plot(Disk_Oxoid,Disk_Mast,Disk_BD)
draw_plot(Disk_BD,"BD")
draw_plot(Disk_Oxoid,"Oxoid")
draw_plot(Disk_Mast,"Mast")



