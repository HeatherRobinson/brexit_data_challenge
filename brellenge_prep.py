#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Make a pivot table from ethnicity-full-nested-new and a metadata table. Explore how pandas and seaborn work a little.

Run with ipython -i or load into Jupyter or whatever.

Created on Sat Mar  3 11:14:51 2018

@author: tcake and cozza
"""

import pandas as pd


def change_since(start, end=2015):
    "Normalised change in population since x till y."
    start = 'y{}'.format(start)
    end = 'y{}'.format(end)
    return (pivoted.loc[:, end] - pivoted.loc[:, start]) / pivoted.loc[:, start]

# Read in data
data = pd.read_csv("data/ethnicity-full-nested-new.csv")
yearlabels = ['y{}'.format(x) for x in range(1998, 2018)]

## Globals to play with

# Make the pivot table
pivoted = pd.pivot_table(data[['AreaName', 'ethnic2'] + yearlabels], columns=['ethnic2'], index = ['AreaName'])
idx = pd.IndexSlice

# Data for joining on: Remove all the ethnicity stuff and drop rate_nonUK because it's got NAs in it.
metadata = data.drop(["ethnic2", "ethnicrate", "rate_nonUk"] + yearlabels,1).drop_duplicates().set_index('AreaName')
# Add a "Result" column for Tess.
metadata["Result"] = metadata.apply(lambda row: "Leave" if row.Leave > row.Remain else "Remain", axis=1)
# Proportion White British in 2015: good for regression with change rate.
metadata['y2015_WBR'] = pivoted.loc[:, idx['y2015', 'White British']]

# List of ethnicities for for loops.
ethnicities = [x for x in pivoted.columns.levels[1]]

### Analysis ###


# How to index pivot table
## First idx is one of the pivot table indexes (pivoted.index.levels), second one is one of the ethnicity columns
pivoted.loc[:, idx['y1998':'y2003', 'Asian':'Other']]


# How to plot:
import matplotlib.pyplot as plt
import seaborn

def stacked_bar_chart():
    pivoted.loc[:,idx[:,:]].dropna().sum().divide(348).unstack('ethnic2').plot.bar(stacked=True, figsize=(10,7), legend =True)

def scatter_plot_change(ethnicity, start, end=2015):
    "Plot change in ethnicity since start against Pct_Remain"
    data = metadata.join(change_since(start, end)[ethnicity]).dropna()
    seaborn.regplot(data[ethnicity], data['Pct_Remain'])

# scatter_plot_change('White Other', 2003)
stacked_bar_chart() # I'm not sure why the bar chart does not remain constant
#plt.show()

# Interactive use:
# df=metadata.join(change_since(2003)).dropna()
# seaborn.regplot(df.Asian, df.Pct_Remain)

# Get an interactive console. Can also use ipython3 -i brellenge_prep.py
# import IPython
# IPython.embed()

# Regression example

import statsmodels.formula.api as smf
df=change_since(2005).join(metadata)

# R2 = 0.45
# The Q is to handle whitespace in column names.
smf.ols('Pct_Remain ~ Q("White British") + Q("White Other") + Asian + Black + Other + Region', data=df).fit().summary()
# R2 = 0.45
smf.ols('Pct_Remain ~ Q("White British") + Q("White Other") + Asian + Black + Other + y2015_WBR', data=df).fit().summary()
