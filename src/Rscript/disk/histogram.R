library(dplyr)
library(ggplot2)
library(statip)
library(lattice)
out <- "./plots/"
if (file.exists(out)){
  setwd(file.path(out))
} else {
  dir.create(file.path(out))
  setwd(file.path(out))
  
}

draw_distribution_plot <- function(Disk_Oxoid,Disk_BD,Disk_Mast){

  combined_data <- rbind( Disk_Oxoid,Disk_BD,Disk_Mast)
  combined_data$Strain_no <- factor(combined_data$Strain_no, levels = unique(combined_data$Strain_no))
  combined_data$Strain_no <- as.factor(combined_data$Strain_no)
  
  combined_data$Disk_diff_Linezolid10 <- as.factor(combined_data$Disk_diff_Linezolid10)
  combined_data <- combined_data %>%
    mutate(data_type = ifelse(Disk_diffusion == "Oxoid", "Oxoid",ifelse(Disk_diffusion == "BD", "BD","Mast" )))
  
  # oobg(file = paste0("histogram_disk.pdf"), width = 24, height = 15)
  plot_combined <- ggplot(combined_data, aes(y = Disk_diff_Linezolid10, fill = data_type)) +
    geom_bar(stat = 'count', position="dodge") + 
    geom_text(stat = 'count', aes(label = ..count..), vjust = 0, size = 3) +  
    coord_flip() +
    facet_wrap(~factor(Strain_no), as.table = TRUE, scales = "free_x") +
    theme(legend.position = "top") +
    theme_bw() 
  ggsave("histogram_disk.png",width = 24, height = 15)
  print(plot_combined)
  dev.off()
  

  
}