library(ggplot2)
library(dplyr)
library(tidyr)


draw_plot <- function(selected_data, type, output_path) {
  if (!dir.exists(output_path)) {
    dir.create(output_path, recursive = TRUE)
  }
  data <- as.data.frame(selected_data[1]) # Extract the first row for demonstration
  n <- as.numeric(selected_data[2])

  df <- data.frame(
    Strain_no = data$Strain_no,
    Species = data$Species,
    mode.log.MIC = as.numeric(data$mode.log.MIC),
    E.log.MIC = as.numeric(data$E.log.MIC),
    lower.log.MIC = as.numeric(data$lower.log.MIC),
    upper.log.MIC = as.numeric(data$upper.log.MIC),
    lower.log.MIC.ref = as.numeric(data$lower.log.MIC.ref),
    upper.log.MIC.ref = as.numeric(data$upper.log.MIC.ref)
  )

  # Create species labels
  species_labels <- ifelse(substr(df$Species, 1, 1) == "1",
    paste(levels(df$Strain_no), "faecalis", sep = " "),
    paste(levels(df$Strain_no), "faecium", sep = " ")
  )

  ggplot(df) +
    geom_hline(yintercept = seq(0.5, n + 0.5, 1), color = "grey90") +
    geom_hline(yintercept = c(10.5, 20.5), linetype = "solid", linewidth = 1) +
    geom_point(aes(x = mode.log.MIC, y = 1:n), shape = 0, linewidth = 2) +
    geom_point(aes(x = E.log.MIC, y = 1:n - 0.25), shape = 15, linewidth = 2) +
    geom_segment(aes(x = lower.log.MIC, xend = upper.log.MIC, y = 1:n - 0.25, yend = 1:n - 0.25)) +
    geom_point(aes(x = lower.log.MIC.ref, y = 1:n + 0.25), color = "black", size = 2) +
    geom_point(aes(x = upper.log.MIC.ref, y = 1:n + 0.25), shape = 16, color = "black", size = 2) +
    geom_segment(aes(x = lower.log.MIC.ref, xend = upper.log.MIC.ref, y = 1:n + 0.25, yend = 1:n + 0.25), color = "black") +
    # Axis labels and title
    scale_x_continuous("MIC", breaks = seq(-1, 9), labels = 2^(-1:9)) +
    scale_y_continuous("", breaks = 1:n, labels = species_labels) +
    labs(title = type) +
    # Theme adjustments
    theme_minimal() +
    theme(
      axis.text.x = element_text(size = 14),
      axis.text.y = element_text(size = 12),
      axis.title.x = element_text(size = 16),
      plot.title = element_text(hjust = 0.5, size = 20),
      plot.margin = unit(c(1, 1, 2, 1), "lines")
    ) +
    scale_shape_manual(name = "Legend", values = c("Mode MICs" = 0, "Mean MICs" = 15, "Reference MICs" = 16)) +
    scale_color_manual(name = "Legend", values = c("Reference MICs" = "black")) +
    scale_linetype_manual(name = "Legend", values = c("Interval censoring" = "solid"))

  # Save the plot to the specified output path
  ggsave(paste0(output_path, "/figure_", type, ".png"), width = 10, height = 8)
}
