library(ggplot2)
setwd("./plots/")
out <- "./plots/"
if (file.exists(out)){
  setwd(file.path(out))
} else {
  dir.create(file.path(out))
  setwd(file.path(out))
  
}

draw_plot <- function(data,name){
  
  df <- data.frame(
    Mean = as.numeric(data$Mean),
    SD = as.numeric(data$SD),
    Lower = as.numeric(data$Lower),
    Upper = as.numeric(data$Upper),
    Strain_no = data$Strain_no,
    K_res =as.numeric(data$K_res),
    EDL = as.numeric(data$EDL),
    max = as.numeric(data$max),
    min = as.numeric(data$min)
  )
  
  d<-0.15
  ggplot(df) +
    geom_point(aes(x = Mean, y = Strain_no, shape = "Mean",color="SD"), size = 2) +
    geom_point(aes(x = SD, y = Strain_no, shape = "SD",color="SD"), size = 2, position = position_nudge(y = d)) +
    geom_errorbarh(aes(xmin = Lower, xmax = Upper, y = Strain_no,color="SD"), height = 0.2) +
    geom_errorbarh(aes(xmin = min, xmax = max, y = Strain_no, color = "Min/Max"), height = 0.2, position = position_nudge(y = +d)) +
    geom_point(aes(x = K_res, y = Strain_no, shape = "K-res", color = "SD"), size = 2, position = position_nudge(y = -d)) +
    geom_point(aes(x = EDL, y = Strain_no, shape = "EDL", color = "SD"), size = 2, position = position_nudge(y = d)) +
    labs(x = "Mean / SD / K_res / EDL", y = "Strain_no", shape = "Variable", title = name, color = "Legend") +
    theme_classic() +
    theme(
      legend.text = element_text(size = 10),
      legend.title = element_text(size = 10),
      legend.position = "right",
      panel.grid.major.x = element_blank(),
      axis.text.y = element_text(margin = margin(0, 15, 0, 0),vjust =-1), 
      panel.grid.major.y = element_line(color = "grey", size = 0.5, linetype = "dotted") 
    ) +
    scale_shape_manual(values = c('Mean' = 15, "SD" = 1, "K-res" = 2, "EDL" = 16),
                       name = "")+
    scale_color_manual(values = c("Min/Max" = "red", "SD" = "black"), name = "Range") +
    scale_x_continuous(breaks = c(seq(0, 34, by = 1)),
                       labels = c(seq(0, 34, by = 1)))
  ggsave( paste0("figure_", name, ".png"), width = 15, height = 10)
}


draw_combine_plot<- function(data,data2,data3){

  data$type <- "Oxoid"
  data2$type <- "Mast"
  data3$type <- "BD"
  
  d<-0.3
  cd <- rbind(data,data2,data3)
  cd <- data.frame(
    Mean = as.numeric(cd$Mean),
    SD = as.numeric(cd$SD),
    Lower = as.numeric(cd$Lower),
    Upper = as.numeric(cd$Upper),
    Strain_no = cd$Strain_no,
    K_res =as.numeric(cd$K_res),
    EDL = as.numeric(cd$EDL),
    max = as.numeric(cd$max),
    min = as.numeric(cd$min),
    type=cd$type
    
  )
  cd <- cd[complete.cases(cd), ]
  cd$type <- factor(cd$type)
  cd$y_nudge <- ifelse(cd$type == "Oxoid", 0.1, ifelse(cd$type == "Mast", -0.3, 0.2))
  
  cd$Strain_no <- reorder(cd$Strain_no, -as.numeric(cd$Strain_no)) 
   ggplot(cd) +
    geom_point(aes(x = Mean, y = Strain_no, shape = "Mean", color = type), size = 2) +
    geom_point(aes(x = SD, y = Strain_no, shape = "SD", color = type), size = 2, position = position_nudge(y = d + cd$y_nudge)) +
    geom_errorbarh(aes(xmin = Lower, xmax = Upper, y = Strain_no, color = type), height = 0.2) +
    geom_errorbarh(aes(xmin = min, xmax = max, y = Strain_no, color = type), height = 0.2, position = position_nudge(y = +d+cd$y_nudge)) +
    geom_point(aes(x = K_res, y = Strain_no, shape = "K-res", color = type), size = 2, position = position_nudge(y = -d+cd$y_nudge)) +
    geom_point(aes(x = EDL, y = Strain_no, shape = "EDL", color = type), size = 2, position = position_nudge(y = d+cd$y_nudge)) +
    
    labs(x = "Mean / SD / K_res / EDL", y = "Strain_no", shape = "Variable", color = "Type") +
     theme_bw() +
    theme(
      legend.text = element_text(size = 10),
      legend.title = element_text(size = 10),
      legend.position = "right",
      panel.grid.major.x = element_blank(),
      axis.text.y = element_text(margin = margin(0, 15, 0, 0), vjust = -2),
      panel.grid.major.y = element_line(color = "grey", size =0.5),
      axis.text.x = element_text(margin = margin(15, 0, 0, 0)),
    ) +
    scale_shape_manual(values = c('Mean' = 15, "SD" = 1, "K-res" = 2, "EDL" = 16),
                       name = "") +
    scale_color_manual(values = c("darkcyan", "royalblue","salmon"), name = "type") +
    scale_x_continuous(breaks = c(seq(0, 34, by = 1)),
                       labels = c(seq(0, 34, by = 1)))
  
  ggsave(paste0("figure_disk_combined.png"), width = 15, height = 15)
  
}


draw_Other <- function(data,name){
  
  df <- data.frame(
    Mean = as.numeric(data$Mean),
    SD = as.numeric(data$SD),
    Lower = as.numeric(data$Lower),
    Upper = as.numeric(data$Upper),
    Strain_no = data$Strain_no,
    K_res =as.numeric(data$K_res),
    EDL = as.numeric(data$EDL),
    max = as.numeric(data$max),
    min = as.numeric(data$min)
  )
  
  d<-0.15
  ggplot(df) +
    geom_point(aes(x = Mean, y = Strain_no, shape = "Mean",color="SD"), size = 2) +
    geom_point(aes(x = SD, y = Strain_no, shape = "SD",color="SD"), size = 2, position = position_nudge(y = d)) +
    geom_errorbarh(aes(xmin = Lower, xmax = Upper, y = Strain_no,color="SD"), height = 0.2) +
    geom_errorbarh(aes(xmin = min, xmax = max, y = Strain_no, color = "Min/Max"), height = 0.2, position = position_nudge(y = +d)) +
    geom_point(aes(x = K_res, y = Strain_no, shape = "K-res", color = "SD"), size = 2, position = position_nudge(y = -d)) +
    geom_point(aes(x = EDL, y = Strain_no, shape = "EDL", color = "SD"), size = 2, position = position_nudge(y = d)) +
    labs(x = "Mean / SD / K_res / EDL", y = "Strain_no", shape = "Variable", title = name, color = "Legend") +
    theme_classic() +
    theme(
      legend.text = element_text(size = 10),
      legend.title = element_text(size = 10),
      legend.position = "right",
      panel.grid.major.x = element_blank(),
      axis.text.y = element_text(margin = margin(0, 15, 0, 0),vjust =-1), 
      panel.grid.major.y = element_line(color = "grey", size = 0.5, linetype = "dotted") 
    ) +
    scale_shape_manual(values = c('Mean' = 15, "SD" = 1, "K-res" = 2, "EDL" = 16),
                       name = "")+
    scale_color_manual(values = c("Min/Max" = "red", "SD" = "black"), name = "Range") +
    scale_x_continuous(breaks = c(seq(0, 34, by = 1)),
                       labels = c(seq(0, 34, by = 1)))
  ggsave( paste0("figure_", name, ".png"), width = 15, height = 10)
  
  
}

