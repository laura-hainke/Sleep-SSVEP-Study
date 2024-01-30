# Author: LH
# Date: 2023-09-26
# Functionality: Functions for statistics_main.R, creating plots
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Packages
library(ggplot2)
library(tidyr)
library(dplyr)
library(reshape2)
library(scales)
library(see)

# Colours for plots
colour_scheme=data.frame(con="#666666",
                         exp="#CC3333",
                         W="#CCCCCC",
                         N1="#ece2f0",
                         N2="#a6bddb",
                         N3="#1c9099",
                         REM="#756bb1")

# Constants
nr_datapoints_SSVEP = 25 # 25 ms segments
nr_conditions = 2 # control, experimental
nr_stages = 4 # W, N2, N3, REM (N1 not included)
base_size = 7 # base size of plot text


# Function: plot_bar_stack -------------------------------------------------------------------------------------------
# Create a stacked bar plot, for % of stages.

## INPUT

# data_long : dataframe
# Dataframe in long format

## OUTPUT

# No values, just plot

plot_bar_stack <- function(data_long) {
  
  ggplot(data_long, aes(x=condition, y=value, fill=variable)) +
    geom_bar(stat="identity", position = position_fill(reverse = TRUE), width=0.5) + # Start with N1
    labs(title="Sleep Stage Distribution", x="Condition", y="Time per Stage (% of TST)", fill="Stage") + # Labels
    scale_fill_manual(values=c(colour_scheme$N1, colour_scheme$N2, colour_scheme$N3, colour_scheme$REM), labels=c("N1","N2","N3","REM")) + # Stage colours & labels
    scale_x_discrete(labels=c("Control","Experimental")) + # X-tick labels
    scale_y_continuous(labels = percent) + # Y-tick values
    theme_minimal(base_size = base_size) + # Background
    coord_flip() + # Flip x & y axes
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          legend.text = element_text(size=rel(1.5)),
          legend.title = element_text(size=rel(1.5)),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm")) # Plot margins
  
}



# Function: plot_box_2X4 -------------------------------------------------------------------------------------------
# Create a set of boxplots for max. 2 conditions X 4 stages.

## INPUT

# data_long : dataframe
# Dataframe in long format

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

plot_box_2X4 <- function(data_long, title_plot, title_y, ymin, ymax) {
  
  ggplot(data_long, aes(x=stage, y=value, fill=condition)) +
    geom_boxplot() + # Show condition pairs per stage
    geom_point(size=1, position=position_dodge(0.75)) + # add individual data points
    stat_summary(fun = "mean", geom = "point", size = 2, color = "white", position = position_dodge(0.75)) + # add mean
    scale_fill_manual(values=c(colour_scheme$con, colour_scheme$exp), labels=c("Control","Experimental")) +
    labs(title=title_plot, x="Stage", y=title_y, fill="Condition") + # Labels
    ylim(ymin, ymax) + # Change y-axis limits
    theme_minimal(base_size = base_size) + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          legend.text = element_text(size=rel(1.5)),
          legend.title = element_text(size=rel(1.5)),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm")) # Plot margins
  
}



# Function: plot_box_1X4 -------------------------------------------------------------------------------------------
# Create a set of boxplots for max. 1 condition X 4 stages, for stimulation time.

## INPUT

# data_long : dataframe
# Dataframe in long format

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

# ymin : int
# Start of y-axis

# ymax : int
# End of y-axis

# limits: vector
# Contains expected maximal stimulation time per stage, in minutes (N2, N3, REM)

## OUTPUT

# No values, just plot

plot_box_1X4 <- function(data_long, title_plot, title_y, ymin, ymax, limits) {
  
  ggplot(data_long, aes(x=stage, y=value, fill=stage)) +
    geom_boxplot(show.legend = FALSE) + 
    geom_point(size=1, position=position_dodge(0.75)) + # add individual data points
    stat_summary(fun = "mean", geom = "point", size = 2, color = "white", position = position_dodge(0.75)) + # add mean
    annotate("segment", x=0.63, y=limits[1], xend=1.38, yend=limits[1], linetype="dashed", color="#333333", linewidth=0.7) + # add max. expected stimulation time for N2
    annotate("segment", x=1.63, y=limits[2], xend=2.38, yend=limits[2], linetype="dashed", color="#333333", linewidth=0.7) + # add max. expected stimulation time for N3
    annotate("segment", x=2.63, y=limits[3], xend=3.38, yend=limits[3], linetype="dashed", color="#333333", linewidth=0.7) + # add max. expected stimulation time for REM
    scale_fill_manual(values=c(colour_scheme$N2, colour_scheme$N3, colour_scheme$REM)) +
    labs(title=title_plot, x="Stage", y=title_y) + # Labels
    ylim(ymin, ymax) + # Change y-axis limits
    theme_minimal(base_size = base_size) + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm"), # Plot margins
          legend.position = "none") 
  
}



# Function: plot_scatter_2X4 -------------------------------------------------------------------------------------------
# Create a connected scatterplot for 2 conditions X 4 stages.

## INPUT

# data_long : dataframe
# Dataframe in long format

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

plot_scatter_2X4 <- function(data_long, title_plot, title_y, ymin, ymax) {
  
  # If it's an SNR plot, a dashed line should be shown at y=1
  if (grepl("SNR", data_long$variable[1]) == TRUE) {
    line_dash_y = 1
  } else {
    line_dash_y = 0
  }
  
  ggplot(data_long, aes(x=condition, y=value, color=ID)) + 
    geom_point(size=4, position=position_dodge(0.03)) +
    geom_line(aes(group = ID), position=position_dodge(0.03), linewidth=1.2) +
    facet_grid(. ~ factor(stage)) + # levels=c("W","N2","N3","REM")
    scale_colour_grey(start=0, end=0.8, guide="none") +
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_x_discrete(expand=c(0.15, 0.15)) + # X-tick labels
    geom_hline(yintercept=line_dash_y, linetype='dashed') + # Line at meaningful point of no effect
    ylim(ymin, ymax) + # Change y-axis limits
    theme_minimal(base_size = base_size) + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          axis.text.x = element_text(colour="grey"),
          strip.text = element_text(face="bold", size=rel(2)), # Facet test
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm")) # Plot margins
  
}



# Function: plot_violin_paired -------------------------------------------------------------------------------------------
# Create violin plots with connected dots.

## INPUT

# data_long : dataframe
# Dataframe in long format

# title_plot : str
# Plot title

# title_y : str
# Y-axis title

## OUTPUT

# No values, just plot

plot_violin_paired <- function(data_long, title_plot, title_y) {
  
  ggplot(data_long, aes(x=condition, y=value)) + 
    geom_violinhalf(aes(fill=condition), flip=1) + # Violin plot shape
    geom_point(color="grey", size=2) + # Data points, jittered
    geom_line(aes(group = ID), color="grey", linewidth=1, linetype="twodash") + # connect paired dots
    stat_summary(fun = "mean", geom="point", shape=18, color = "black", size=5) + # Add mean as point
    labs(title=title_plot, x="Condition", y=title_y) + # Labels
    scale_fill_manual(values=c(colour_scheme$con, colour_scheme$exp), guide="none") + # Condition colours, remove legend
    scale_x_discrete(labels=c("Control","Experimental")) + # X-tick labels
    theme_minimal(base_size=base_size) + # Background
    theme(axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=2),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3)),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm")) # Plot margins
  
}



# Function: plot_n_SSVEPs ----------------------------------------------------------------------------------------------------------------------
# Create a big plot with SSVEPs for all subjects, 1 condition and 1 stage.

## INPUT

# data_long : dataframe
# Dataframe in long format, containing time series data

# title_plot : str
# Plot title

# colour : str
# Element of colour_scheme; colour of SSVEP lines

# ymax : int
# Half of y-axis range

## OUTPUT

# No values, just plot

plot_n_SSVEPs <- function(data_long, title_plot, colour, ymax) {
  
  ggplot(data_long, aes(x=time, y=value)) +
    geom_line(color=colour, linewidth=1) +
    facet_wrap(~ID, ncol=5) +
    labs(title=title_plot, y="Amplitude (uV)", x="Time (ms)") +
    scale_x_continuous(limits=c(0,25), breaks=c(0,25)) +
    scale_y_continuous(limits=c(-ymax,ymax), breaks=c(-ymax,0,ymax)) +
    theme_minimal(base_size=base_size) +
    theme(panel.grid.minor = element_blank(), # remove background lines
          strip.text.x = element_text(size=rel(1.5), face="bold"),
          axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=1.5),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3), vjust=1.5),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm"))
}



# Function: plot_avg_SSVEPs_stage ----------------------------------------------------------------------------------------------------------------------
# Create a plot with grand average SSVEPs by stage, each plot with both conditions.

## INPUT

# data_long : dataframe
# Dataframe in long format, containing grand average data

# title_plot : str
# Plot title

## OUTPUT

# No values, just plot

plot_avg_SSVEPs_stage <- function(data_long, title_plot) {

  ggplot(data_long, aes(x=time, y=value, color=condition)) +
    geom_line(linewidth=1) +
    facet_grid(~factor(stage)) + 
    labs(title=title_plot, y="Amplitude (uV)", x="Time (ms)") +
    scale_x_continuous(limits=c(0,25), breaks=c(0,25)) +
    scale_color_manual(name="Condition", values=c(colour_scheme$con,colour_scheme$exp), labels=c("Control","Experimental")) +
    theme_minimal(base_size=base_size) +
    theme(panel.grid.minor = element_blank(), # remove background lines
          strip.text.x = element_text(size=rel(2), face="bold"),
          axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=1.5),
          axis.text = element_text(size=rel(1.5)), 
          legend.text = element_text(size=rel(1.5)),
          legend.title = element_text(size=rel(1.5)),
          plot.title = element_text(size=rel(3), vjust=1.5),
          plot.margin = margin(0.5,0.5,0.5,0.5,"cm"))

}



# Function: plot_SSVEPs_n_avg ----------------------------------------------------------------------------------------------------------------------
# Create a plot with SSVEPs for all subjects + grand average, both conditions, 1 stage.

## INPUT

# data_timeseries, : dataframe
# Dataframe in long format, containing time series data for 1 stage

# data_grand_average : dataframe
# Dataframe in long format, containing grand average for 1 stage

# title_plot : str
# Plot title

## OUTPUT

# No values, just plot

plot_SSVEPs_n_avg <- function(data_timeseries, data_grand_average, title_plot) {
  
  ggplot(data_timeseries, aes(x=time, y=value, fill=ID)) +
    geom_line(color="#CCCCCC", linewidth=0.5) + # plot each subject's SSVEPs
    geom_line(data=data_grand_average, aes(x=time,y=value,fill=NULL), linewidth=1) + # add grand average for given stage & condition
    facet_wrap(~factor(condition,labels=c("Control","Experimental")), ncol=2) +
    labs(title=title_plot, y="Amplitude (uV)", x="Time (ms)") +
    scale_x_continuous(limits=c(0,25), breaks=c(0,25)) +
    theme_minimal(base_size=base_size) +
    theme(panel.grid.minor = element_blank(), # remove background lines
          strip.text.x = element_text(size=rel(3), face="bold"),
          axis.title.x = element_text(size=rel(2), vjust=-1), # Label sizes, relative
          axis.title.y = element_text(size=rel(2), vjust=1.5),
          axis.text = element_text(size=rel(1.5)), 
          plot.title = element_text(size=rel(3), vjust=1.5),
          plot.margin = margin(0.5,0.5,0.5,0.5, "cm"))
}

