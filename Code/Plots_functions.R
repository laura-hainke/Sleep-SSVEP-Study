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

# Colour schemes
col_con = "#2b8cbe" # control
col_exp = "#2ca25f" # experimental
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
    stat_summary(fun = "mean", geom = "crossbar", color = "black", width=0.3) + # Add mean as line
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



# Function: plot_bar_anova -------------------------------------------------------------------------------------------
# Create a bar plot for a 4X2 ANOVA.

## INPUT

# data : dataframe
# Dataframe containing 9 columns: ID, variables 1 - 8

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_bar_anova <- function(data, title_plot, title_y) {
  
  # Convert data into long format
  data_long = melt(data, id.vars="ID", variable.name="condition", value.name="value")
  
  # Split condition column into stage & condition
  data_long = separate_wider_delim(data_long, cols = condition, delim = "_", names = c("stage","variable","condition"))
  
  # Invert value variable polarity
  data_long$value = data_long$value * -1
  
  # Create figure
  ggplot(data_long, aes(x=stage, y=value, fill=condition)) +
    geom_bar(stat="identity", position = "dodge", width=0.5) + # Show condition pairs per stage
    scale_x_discrete(limits=c("W","N2","N3","REM")) +
    # scale_fill_manual(values=c(col_W, col_N2, col_N3, col_REM)) +
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