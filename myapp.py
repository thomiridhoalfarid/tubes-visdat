#!/usr/bin/env python
# coding: utf-8

# # Visualisasi Interaktif COVID-19 di Indonesia

# In[1]:


import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
# from bokeh.palettes import Spectral6
from bokeh.layouts import widgetbox, row
from bokeh.models import Select, RangeSlider

from datetime import date, datetime



# ## Load Dataset

cov_data = pd.read_csv('data/covid_19_indonesia_time_series_all.csv')
cov_data.head()

# ## Preprocessing Data

# Selecting column usage
df = cov_data.iloc[:,:12]

# remove data with location level = Country
idx = df[df['Location Level'] == 'Country'].index
df.drop(idx, axis=0, inplace=True)




# remove unused columns
col = ['Location ISO Code', 'New Cases', 'New Deaths', 'New Recovered', 'New Active Cases', 'Location Level']
df.drop(col, axis=1, inplace=True)

# rename columns
col = {
    'Total Cases': 'Total_Cases', 
    'Total Deaths': 'Total_Deaths', 
    'Total Recovered': 'Total_Recovered', 
    'Total Active Cases': 'Total_Active_Cases'}
df.rename(col, axis=1, inplace=True)



# convert string to datetime for column Date
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

# make a new column for month and year
df['month'] = pd.DatetimeIndex(df['Date']).month
df['year'] = pd.DatetimeIndex(df['Date']).year



# ## Bokeh Data Visualization


# Make a list of the unique values from index (provinsi)
prov_list = list(df.Location.unique())

# Make a color mapper: color_mapper
color_mapper = CategoricalColorMapper(factors=prov_list)

#Change datatype year from int to str
df['year'] = df['year'].apply(str)


# Make the ColumndfSource: source
source = ColumnDataSource(data={
    'x'       : df['Date'].loc[(df.Location == 'DKI Jakarta') & (df.month.isin([i for i in range(3,6)])) & (df.year == '2020')],
    'y'       : df['Total_Deaths'].loc[(df.Location == 'DKI Jakarta') & (df.month.isin([i for i in range(3,6)])) & (df.year == '2020')]
    })


#Callback for updating data
def callback(attr, old, new):
    minMonth, maxMonth = slider.value
    selectedLocation = loc_select.value
    selectedData = data_select.value
    selectedYear = yr_select.value

    # Label axes of plot
    plot.yaxis.axis_label = selectedData

    # new data
    new_data = {
        'x'       : df['Date'].loc[(df.Location == selectedLocation) & (df.month.isin([i for i in range(int(minMonth),int(maxMonth+1))])) & (df.year == selectedYear)],
        'y'       : df[selectedData].loc[(df.Location == selectedLocation) & (df.month.isin([i for i in range(int(minMonth),int(maxMonth+1))])) & (df.year == selectedYear)]
    }
    # updating source data to new data
    source.data = new_data




#Plotting

#Define figure usage
plot = figure(title='Visualisasi Covid-19 per Provinsi', x_axis_label='Date', x_axis_type="datetime", y_axis_label='Total_Deaths',
           plot_height=400, plot_width=700)

# plotting for line chart
plot.line(x='x', y='y', source=source)

#adding tools to chart
plot.add_tools(HoverTool(
    tooltips=[
        ( 'date','@x{%F}'),
        ( 'Value', '@y'),
    ],

    formatters={
        '@x'      : 'datetime', # use 'datetime' formatter for 'date' field
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
))



# ##Bokeh widget

#RangeSlider for selectedMonth
slider = RangeSlider(start=1, end=12, step=1, value=(3,5), title='Bulan')
slider.on_change('value',callback)


#Dropdown for selectedLocation
loc_select = Select(
    options= list(df.Location.unique()),
    value='DKI Jakarta',
    title='Provinsi'
)
loc_select.on_change('value', callback)

#Dropdown for selectedYear
yr_select = Select(
    options= ['2020','2021'],
    value='2020',
    title='Tahun'
)
yr_select.on_change('value', callback)

#Dropdown for selectedData
data_select = Select(
    options= ["Total_Cases","Total_Deaths","Total_Recovered","Total_Active_Cases"],
    value='Total_Deaths',
    title='Data Covid-19'
)
data_select.on_change('value', callback)


# Creating layout
layout = row(widgetbox(yr_select,slider,loc_select,data_select), plot)
curdoc().add_root(layout)
curdoc().title = 'Visualisasi Covid-19 per Provinsi'

show(layout)
