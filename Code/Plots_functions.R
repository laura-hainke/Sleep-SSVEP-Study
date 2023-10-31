# Author: LH
# Date: 2023-09-26
# Functionality: Functions for statistics_main.R, plots
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Packages
library(ggplot2)
library(tidyr)
library(dplyr)
library(reshape2)
library(scales)
library(see)

# Colour schemes
col_con = "#666666" # control
col_exp = "#CC3333" # experimental
col_W = "grey"
col_N1 = "#ece2f0"
col_N2 = "#a6bddb"
col_N3 = "#1c9099"
col_REM = "#756bb1"



# Function: plot_violin -------------------------------------------------------------------------------------------
# Create a violin plot.

## INPUT

# data : dataframe
# Dataframe containing 3 columns: ID, variable 1, variable 2

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_violin <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Calculate values for error bars
  errbar_lims <- group_by(data_long, condition) %>% 
    summarize(mean=mean(value), se=sd(value)/sqrt(n()), 
              upper=mean+(2*se), lower=mean-(2*se))
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value)) + 
    geom_violin(aes(fill=condition), width=0.5) + # Violin plot shape
    geom_point(color="black", size=2, position = position_jitter(w=0.05, h=0)) + # Data points, jittered
    stat_summary(fun = "mean", geom = "crossbar", color = "black", width=0.5) + # Add mean as line
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_fill_manual(values=c(col_con, col_exp), guide="none") + # Condition colours, remove legend
    scale_x_discrete(labels=c("Control","Experimental")) + # X-tick labels
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}



# Function: plot_scatter -------------------------------------------------------------------------------------------
# Create a connected scatterplot.

## INPUT

# data : dataframe
# Dataframe containing 3 columns: ID, variable 1, variable 2

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_scatter <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value, color=ID)) + 
    geom_point(size=4, position=position_dodge(0.03)) +
    geom_line(aes(group = ID), position=position_dodge(0.03), linewidth=1.2) +
    scale_colour_grey(start=0, end=0.8, guide="none") +
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_x_discrete(labels=c("Control","Experimental"), expand=c(0.15, 0.15)) + # X-tick labels
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}



# Function: plot_bar_stack -------------------------------------------------------------------------------------------
# Create a stacked bar plot, for % of stages.

## INPUT

# data : dataframe
# Dataframe containing 9 columns: ID, variables 1 - 8

## OUTPUT

# No values, just plot

plot_bar_stack <- function(data) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Split condition column into stage & condition
  data_long = separate_wider_delim(data_long, cols = condition, delim = "_", names = c("stage","condition"))
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value, fill=stage)) +
    geom_bar(stat="identity", position = position_fill(reverse = TRUE), width=0.5) + # Start with N1
    labs(title="Sleep Stage Distribution", x="Condition", y="Time per Stage (% of TST)", fill="Stage") + # Labels
    scale_fill_manual(values=c(col_N1, col_N2, col_N3, col_REM), labels=c("N1","N2","N3","REM")) + # Stage colours & labels
    scale_x_discrete(labels=c("Control","Experimental")) + # X-tick labels
    scale_y_continuous(labels = percent) + # Y-tick values
    theme_minimal() + # Background
    coord_flip() + # Flip x & y axes
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          legend.text = element_text(size=15),
          legend.title = element_text(size=15),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}



# Function: plot_violin_paired -------------------------------------------------------------------------------------------
# Create violin plots with connected dots.

## INPUT

# data : dataframe
# Dataframe containing 3 columns: ID, variable 1, variable 2

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_violin_paired <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value)) + 
    geom_violinhalf(aes(fill=condition), flip=1) + # Violin plot shape
    geom_point(color="grey", size=2) + # Data points, jittered
    geom_line(aes(group = ID), color="grey", linewidth=1, linetype="twodash") + # connect paired dots
    stat_summary(fun = "mean", geom="point", shape=18, color = "black", size=5) + # Add mean as line
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_fill_manual(values=c(col_con, col_exp), guide="none") + # Condition colours, remove legend
    scale_x_discrete(labels=c("Control","Experimental")) + # X-tick labels
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}



# Function: plot_box_anova -------------------------------------------------------------------------------------------
# Create a set of boxplots for a 4X2 ANOVA.

## INPUT

# data : dataframe
# Dataframe containing 9 columns: ID, variables 1 - 8

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_box_anova <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Split condition column into stage & condition
  data_long = separate_wider_delim(data_long, cols = condition, delim = "_", names = c("stage","variable","condition"))
  
  # Create figure
  ggplot(data_long, aes(x=stage, y=value, fill=condition)) +
    geom_boxplot() + # Show condition pairs per stage
    geom_point(size=1, position=position_dodge(0.75)) + # add individual data points
    stat_summary(fun = "mean", geom = "point", size = 2, color = "white", position = position_dodge(0.75)) + # add mean
    scale_x_discrete(limits=c("W","N2","N3","REM")) +
    scale_fill_manual(values=c(col_con, col_exp), labels=c("Control","Experimental")) +
    labs(title=title_plot, x="Stage", y=title_y, fill="Condition") + # Labels
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          legend.text = element_text(size=15),
          legend.title = element_text(size=15),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
  
}



# Function: plot_scatter_SNR -------------------------------------------------------------------------------------------
# Create a connected scatterplot for 2 conditions X 4 stages, SNR variables.

## INPUT

# data : dataframe
# Dataframe containing 9 columns: ID, variables 1 - 8

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_scatter_SNR <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Split condition column into stage & condition
  data_long = separate_wider_delim(data_long, cols = condition, delim = "_", names = c("stage","variable","condition"))
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value, color=ID)) + 
    geom_point(size=4, position=position_dodge(0.03)) +
    geom_line(aes(group = ID), position=position_dodge(0.03), linewidth=1.2) +
    facet_grid(. ~ factor(stage,levels=c("W","N2","N3","REM"))) +
    scale_colour_grey(start=0, end=0.8, guide="none") +
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_x_discrete(expand=c(0.15, 0.15)) + # X-tick labels
    geom_hline(yintercept=1, linetype='dashed') + # Line at SNR=1
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          axis.text.x = element_text(colour="grey"),
          strip.text = element_text(face="bold", size=rel(2)), # Facet test
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}
  
  

# Function: plot_scatter_main -------------------------------------------------------------------------------------------
# Create a connected scatterplot for 2 conditions X 4 stages, main variables.

## INPUT

# data : dataframe
# Dataframe containing 9 columns: ID, variables 1 - 8

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

# ymin : int
# Start of y-axis

# ymax : int
# End of y-axis

## OUTPUT

# No values, just plot

plot_scatter_main <- function(data, title_plot, title_y, ymin, ymax) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Split condition column into stage & condition
  data_long = separate_wider_delim(data_long, cols = condition, delim = "_", names = c("stage","variable","condition"))
  
  # Create figure
  ggplot(data_long, aes(x=condition, y=value, color=ID)) + 
    geom_point(size=4, position=position_dodge(0.03)) +
    geom_line(aes(group = ID), position=position_dodge(0.03), linewidth=1.2) +
    facet_grid(. ~ factor(stage,levels=c("W","N2","N3","REM"))) +
    scale_colour_grey(start=0, end=0.8, guide="none") +
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_x_discrete(expand=c(0.15, 0.15)) + # X-tick labels
    ylim(ymin, ymax) + # Change y-axis limits
    theme_minimal() + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          axis.text.x = element_text(colour="grey"),
          strip.text = element_text(face="bold", size=rel(2)), # Facet test
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(1,1,1,1, "cm")) # Plot margins
  
}
  