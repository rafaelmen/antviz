# AntViz Application Developed by Rafael Mendez rmendez@g.harvard.edu
# This application utilizes the Bokeh Visualization Library
# All and data comes from Antweb.org: https://www.antweb.org/api.do


import numpy as np
from bokeh.layouts import row, widgetbox
from bokeh.models import (
    HoverTool,
    OpenURL,
    TapTool,
    BoxZoomTool,
    ResetTool,
    PanTool,
    WheelZoomTool,
    SaveTool,
    ColumnDataSource,
    NumeralTickFormatter,
    LinearColorMapper,
    BasicTicker,
    ColorBar,
)
from bokeh.plotting import curdoc,figure
from bokeh.models.widgets import Select, RangeSlider, Tabs, Panel
import pandas as pd
from math import pi
import json


### Global Styles
fig_width = 1000  # sets width for all plots
fig_height = 600  # sets height for all plots
x_angle = pi / 4  # sets angle for x-axis
sizing_mode = 'scale_width'
primary_color = 'rgba(95, 158, 160, 0.8)'
secondary_color = 'rgba(158,202,225, 0.8)'
border_color = 'rgba(142, 140, 132, 0.8)'
background_color = '#E9ECEF'
choropleth_colors = ["#F8DDDD", "#F6D5D5", "#F4CACA", "#F1BDBD", "#EEACAC",
                     "#EA9797", "#E57D7D", "#DE5C5C", "#D63333","#CC0000"]


### Tab 1: Species Density Map
# basemap data from Ken Alger/Treehouse: https://teamtreehouse.com/library/data-visualization-with-bokeh
with open('antviz/data/countries_geo.json') as json_file:
    json_data = json.load(json_file)
# load csv for country codes
df_codes = pd.read_csv('antviz/data/country_codes.csv', encoding='latin-1')
# load and clean antweb data
geolocales_raw_df = pd.read_csv('antviz/data/antviz_choropleth.csv', error_bad_lines=False)
geolocales_df = geolocales_raw_df[geolocales_raw_df['country'] == geolocales_raw_df['name']]
geolocales_df = geolocales_df[['country', 'endemicSpeciesCount','introducedSpeciesCount', 'speciesCount' ]]
geolocales_df = geolocales_df[pd.notnull(geolocales_df['speciesCount'])]
geolocales_df = geolocales_df.drop_duplicates(subset='country', keep='first')
geolocales_df.columns = ['country_name', 'endemicSpeciesCount', 'introducedSpeciesCount', 'speciesCount']

# get_coordinates function from Ken Alger/Treehouse: https://teamtreehouse.com/library/data-visualization-with-bokeh
def get_coordinates(features):
   depth = lambda L: isinstance(L, list) and max(map(depth, L))+1
   country_id = []
   longitudes = []
   latitudes = []

   for feature in json_data['features']:
       coordinates = feature['geometry']['coordinates']
       number_dimensions = depth(coordinates)
       # one border
       if number_dimensions == 3:
           country_id.append(feature['id'])
           points = np.array(coordinates[0], 'f')
           longitudes.append(points[:, 0])
           latitudes.append(points[:, 1])
       # several borders
       else:
           for shape in coordinates:
               country_id.append(feature['id'])
               points = np.array(shape[0], 'f')
               longitudes.append(points[:, 0])
               latitudes.append(points[:, 1])
   return country_id, longitudes, latitudes

country_id, lats, longs = get_coordinates(json_data['features'])

country_coords = []

for index, country in enumerate(country_id):
    land_mass = {'country_code': country, 'latitudes': lats[index],
                 'longitudes': longs[index]}
    country_coords.append(land_mass)

country_maps = pd.DataFrame(country_coords)

# merge lat/long data with country codes
world_map_with_data = pd.merge(country_maps, df_codes, on='country_code')
# merge lat/long data with antweb codes
world_map_with_data_full = pd.merge(world_map_with_data, geolocales_df, on='country_name', how="left")

def make_plot_map(mapper, tooltips_map, species_val, species_title):
    mapper = mapper
    map_data = ColumnDataSource(world_map_with_data_full)
    tooltips = tooltips_map
    hov = HoverTool(tooltips=tooltips, mode='mouse')
    p_map = figure(plot_width=fig_width, plot_height=fig_height, title= species_title + " Density By Country",
                   tools=[hov, PanTool(), BoxZoomTool(), WheelZoomTool(), SaveTool(), ResetTool()],
                   x_range=(-180, 180),
                   y_range=(-90, 90))
    p_map.patches(xs='latitudes',
                  ys='longitudes',
                  source=map_data,
                  fill_color={'field': species_val, 'transform': mapper},
                  line_color=border_color,
                  fill_alpha=1,
                  line_width=1)
    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="8pt",
                         ticker=BasicTicker(desired_num_ticks=len(choropleth_colors)),
                         formatter=NumeralTickFormatter(format="0,0"),
                         label_standoff=9, border_line_color=None, location=(0, 0))
    color_bar.background_fill_color = background_color
    p_map.add_layout(color_bar, 'left')
    return p_map

def update_plot_map():
    species_val = species_dropdown.value
    if species_val == 'Species (Valid and Morphotaxon)':
        mapper = LinearColorMapper(palette=choropleth_colors, low=world_map_with_data_full.speciesCount.min(),
                                   high=world_map_with_data_full.speciesCount.max())
        tooltips_map = [("Country", "@country_name"), ("Country Code", "@country_code"),
                        ("Species Count", "@speciesCount"), ]
        species_val = 'speciesCount'
        species_title = 'Species (Valid and Morphotaxon)'
    if species_val == 'Endemic':
        mapper = LinearColorMapper(palette=choropleth_colors, low=world_map_with_data_full.endemicSpeciesCount.min(),
                                   high=world_map_with_data_full.endemicSpeciesCount.max())
        tooltips_map = [("Country", "@country_name"), ("Country Code", "@country_code"),
                        ("Endemic Species Count", "@endemicSpeciesCount"), ]
        species_val = 'endemicSpeciesCount'
        species_title = 'Endemic Species'
    if species_val == 'Introduced':
        mapper = LinearColorMapper(palette=choropleth_colors,
                                   low=world_map_with_data_full.introducedSpeciesCount.min(),
                                   high=world_map_with_data_full.introducedSpeciesCount.max())
        tooltips_map = [("Country", "@country_name"), ("Country Code", "@country_code"),
                        ("Introduced Species Count", "@introducedSpeciesCount"), ]
        species_val = 'introducedSpeciesCount'
        species_title = 'Introduced Species'
    layout_map.children[0] = make_plot_map(mapper, tooltips_map, species_val, species_title)

# create widgets_map
species_dropdown = Select(title="Species Dimension:", value='Species (Valid and Morphotaxon)',
                          options=['Species (Valid and Morphotaxon)','Endemic', 'Introduced'])

# create plot_map
mapper = LinearColorMapper(palette=choropleth_colors, low=world_map_with_data_full.speciesCount.min(),
                               high=world_map_with_data_full.speciesCount.max())
tooltips_map = [("Country", "@country_name"), ("Country Code", "@country_code"), ("Species Count", "@speciesCount"), ]
species_val = 'speciesCount'
species_title = 'Species (Valid and Morphotaxon)'
plot_map = make_plot_map(mapper, tooltips_map, species_val, species_title)

# add controls_map
controls_map = [species_dropdown]
for control_map in controls_map:
    control_map.on_change('value', lambda attr, old, new: update_plot_map())

inputs_map = widgetbox(*controls_map, sizing_mode=sizing_mode)

# add layout_map
layout_map = row(plot_map, inputs_map)
tab1 = Panel(child=layout_map, title="Species Density")


### Tab 2: Specimens Overview
df_specimens_overview = pd.read_csv('antviz/data/specimens_all.csv', error_bad_lines=False)
df_specimens_overview = df_specimens_overview.astype(str)
df_specimens_overview = df_specimens_overview.replace('indet', 'unidentified')
df_specimens_overview = df_specimens_overview.replace('(indet)', 'unidentified')
df_specimens_overview = df_specimens_overview.replace('None', 'Unidentified')
df_specimens_overview['monthCollected'] = df_specimens_overview.dateCollected.str[:7]
df_specimens_overview['yearCollected'] = df_specimens_overview.dateCollected.str[:4]
df_specimens_overview['subfamily'] = df_specimens_overview['subfamily'].str.capitalize()

def make_plot_specimens_overview(df,x_val,x_range_val,label, filters_title, tooltips):
    hov = HoverTool(tooltips=tooltips, mode='vline')
    p_specimens_overview = figure(x_range=x_range_val, title=str(len(df)) + ' Specimen Records Found' + filters_title,
                x_axis_label=label, y_axis_label='Specimens',
                width=fig_width, height=fig_height, tools=[hov, PanTool(), BoxZoomTool(),
                                                           WheelZoomTool(), SaveTool(), ResetTool()])
    p_specimens_overview.vbar(x=x_val, width=0.9, bottom=0, top='code', color=primary_color,
            source=df.groupby(x_val).count(), legend=dict(value="Specimens Collected"))
    p_specimens_overview.xaxis.major_label_orientation = x_angle
    p_specimens_overview.xgrid.grid_line_color = None
    p_specimens_overview.ygrid.grid_line_color = '#BFBFBF'
    p_specimens_overview.y_range.start = 0
    p_specimens_overview.yaxis[0].formatter = NumeralTickFormatter(format="0")
    p_specimens_overview.legend.click_policy = 'hide'
    return p_specimens_overview

def update_plot_specimens_overview():
    dimension_select = x_select.value
    min_date_select = range_slider.value[0]
    max_date_select = range_slider.value[-1]
    country_select = countryselect.value
    subfamily_select = subfamilyselect.value
    if country_select == none and subfamily_select == none:
        updated_df = df_specimens_overview[
            (df_specimens_overview['yearCollected'] >= str(min_date_select)) &
            (df_specimens_overview['yearCollected'] <= str(max_date_select))].copy()
        filters_title = ''
    if country_select != none and subfamily_select == none:
        updated_df = df_specimens_overview[
            (df_specimens_overview['yearCollected'] >= str(min_date_select)) &
            (df_specimens_overview['yearCollected'] <= str(max_date_select)) &
            (df_specimens_overview.country == country_select)].copy()
        filters_title = ' In ' + country_select
    if country_select == none and subfamily_select != none:
        updated_df = df_specimens_overview[
            (df_specimens_overview['yearCollected'] >= str(min_date_select)) &
            (df_specimens_overview['yearCollected'] <= str(max_date_select)) &
            (df_specimens_overview.subfamily == subfamily_select)].copy()
        filters_title = ' For The ' + subfamily_select + ' Subfamily'
    if country_select != none and subfamily_select != none:
        updated_df = df_specimens_overview[
            (df_specimens_overview['yearCollected'] >= str(min_date_select)) &
            (df_specimens_overview['yearCollected'] <= str(max_date_select)) &
            (df_specimens_overview.country == country_select) &
            (df_specimens_overview.subfamily == subfamily_select)].copy()
        filters_title = ' In ' + country_select + ' For The ' + subfamily_select + ' Subfamily'
    if dimension_select == 'Month Collected':
        x_val = 'monthCollected'
        x_range_val = sorted(updated_df.monthCollected.unique())
        label = 'Month Specimens Collected'
        tooltips = [("Month Collected", "@monthCollected"),("Specimens Count", "@code"), ]
    if dimension_select == 'Country':
        x_val = 'country'
        x_range_val = sorted(updated_df.country.unique())
        label = 'Country'
        tooltips = [("Country", "@country"),("Specimens Count", "@code"), ]
    if dimension_select == 'Bioregion':
        x_val = 'biogeographicregion'
        x_range_val = sorted(updated_df.biogeographicregion.unique())
        label = 'Bioregion'
        tooltips = [("Bioregion", "@biogeographicregion"), ("Specimens Count", "@code"), ]
    if dimension_select == 'Institution':
        x_val = 'ownedby'
        x_range_val = sorted(updated_df.ownedby.unique())
        label = 'Institution'
        tooltips = [("Institution", "@ownedby"), ("Specimens Count", "@code"), ]
    if dimension_select == 'Scientist':
        x_val = 'collectedby'
        x_range_val = sorted(updated_df.collectedby.unique())
        label = 'Scientist'
        tooltips = [("Scientist", "@collectedby"), ("Specimens Count", "@code"), ]
    if dimension_select == 'Subfamily':
        x_val = 'subfamily'
        x_range_val = sorted(updated_df.subfamily.unique())
        label = 'Subfamily'
        tooltips = [("Subfamily", "@subfamily"), ("Specimens Count", "@code"), ]
    # update the layout by replacing the previous chart
    layout_specimens_overview.children[0] = make_plot_specimens_overview(updated_df, x_val, x_range_val,label, filters_title, tooltips)

# create specimens overview widgets
none = 'No Filter'
x_select = Select(title='Primary Dimension:', value='Country',
                  options=['Country','Bioregion','Institution','Scientist','Subfamily'])
startlist = sorted(df_specimens_overview['yearCollected'].unique().tolist())
range_slider = RangeSlider(start=int(startlist[0]), end=int(startlist[-1]),
                           value=((int(startlist[-2])), (int(startlist[-1]))),
                           step=1, title="Date Collected Range")
countrylist = sorted(df_specimens_overview['country'].unique().tolist())
countrylist.insert(0, none)
countryselect = Select(title="Country Filter:", value=none, options=countrylist)
subfamilylist = sorted(df_specimens_overview['subfamily'].unique().tolist())
subfamilylist.insert(0, none)
subfamilyselect = Select(title="Subfamily Filter:", value=none, options=subfamilylist)

# create specimens overview plot
x_val = 'country'
updated_df = df_specimens_overview[(df_specimens_overview['yearCollected'] >= str(2017)) &
                                   (df_specimens_overview['yearCollected'] <= str(2018))].copy()
x_range_val = sorted(updated_df.country.unique())
label='Country'
filters_title=''
tooltips = [("Country", "@country"),("Specimens Count", "@code"), ]
plot_specimens_overview = make_plot_specimens_overview(updated_df, x_val, x_range_val, label, filters_title, tooltips)

# add specimens overview controls
controls_specimens_overview = [x_select, range_slider, countryselect, subfamilyselect]
for control in controls_specimens_overview:
    control.on_change('value', lambda attr, old, new: update_plot_specimens_overview())

inputs_specimes_overview = widgetbox(*controls_specimens_overview, sizing_mode=sizing_mode)

# add specimens overview layout
layout_specimens_overview = row(plot_specimens_overview, inputs_specimes_overview)
tab2 = Panel(child=layout_specimens_overview, title="Specimens Overview")


### Tab 3: Bioregion Overview
df_bio = pd.read_csv('antviz/data/antviz_species_by_bioregion.csv')

def make_plot_bio_overview(df, x_val, label_bio_overview, tooltips_bio_overview):
    hov_bio_overview = HoverTool(tooltips=tooltips_bio_overview, mode='mouse')
    p_bio_overview = figure(y_range=sorted(df.name, reverse=True), title=label_bio_overview + ' by Bioregion',
                            width=fig_width, height=fig_height, x_axis_label=label_bio_overview,
                            y_axis_label="Bioregion",
                            tools=[hov_bio_overview, TapTool(), BoxZoomTool(),
                                   WheelZoomTool(), SaveTool(), ResetTool()])
    p_bio_overview.hbar(y='name', height=0.9, left=0, right=x_val, color=primary_color, source=df)
    p_bio_overview.xaxis.major_label_orientation = x_angle
    p_bio_overview.xgrid.grid_line_color = None
    p_bio_overview.ygrid.grid_line_color = '#BFBFBF'
    p_bio_overview.x_range.start = 0
    p_bio_overview.yaxis.minor_tick_line_color = None
    p_bio_overview.xaxis[0].formatter = NumeralTickFormatter(format="0")
    p_bio_overview_url = "https://www.antweb.org/bioregion.do?name=@name"
    taptoo1__bio_overview = p_bio_overview.select(type=TapTool)
    taptoo1__bio_overview.callback = OpenURL(url=p_bio_overview_url)
    return p_bio_overview

def update_plot_bio_overview():
    xvalue_select = xval_dropdown.value
    if xvalue_select == 'Species Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'speciesCount'
        label_bio_overview = 'Species Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Species Count", "@speciesCount"), ]
    if xvalue_select == 'Genus Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'genusCount'
        label_bio_overview = 'Genus Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Genus Count", "@genusCount"), ]
    if xvalue_select == 'Specimen Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'specimenCount'
        label_bio_overview = 'Specimen Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Specimen Count", "@specimenCount"), ]
    if xvalue_select == 'Subfamily Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'subfamilyCount'
        label_bio_overview = 'Subfamily Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Subfamily Count", "@subfamilyCount"), ]
    if xvalue_select == 'Image Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'imageCount'
        label_bio_overview = 'Image Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Image Count", "@imageCount"), ]
    if xvalue_select == 'Imaged Specimen Count':
        updated_df_bio_overview = df_bio.copy()
        x_val = 'imagedSpecimenCount'
        label_bio_overview = 'Imaged Specimen Count'
        tooltips_bio_overview = [("Bioregion", "@name"), ("Image Specimen Count", "@imagedSpecimenCount"), ]
    layout_bio_overview.children[0] = make_plot_bio_overview(updated_df_bio_overview, x_val,
                                                             label_bio_overview, tooltips_bio_overview)

# create bioregion overview widgets
xval_dropdown = Select(title="Primary Dimension:", value='speciesCount',
                           options=['Species Count','Genus Count', 'Specimen Count',
                                    'Subfamily Count', 'Image Count', 'Imaged Specimen Count'])

#create bioregion overview plot
updated_df_bio_overview = df_bio.copy()
x_val = 'speciesCount'
label_bio_overview = 'Species Count'
tooltips_bio_overview = [("Bioregion", "@name"), ("Species Count", "@speciesCount"), ]
plot_bio_overview = make_plot_bio_overview(updated_df_bio_overview, x_val, label_bio_overview, tooltips_bio_overview)

#add bioregion overview controls
controls_bio_overview = [xval_dropdown]
for control_bio_overview in controls_bio_overview:
    control_bio_overview.on_change('value', lambda attr, old, new: update_plot_bio_overview())

inputs_bio_overview = widgetbox(*controls_bio_overview, sizing_mode=sizing_mode)

#add bioregion overview layout
layout_bio_overview = row(plot_bio_overview, inputs_bio_overview)
tab3 = Panel(child=layout_bio_overview, title="Bioregion Overview")


### Tab 4: Unique Species By Bioregion
df_sb = pd.read_csv('antviz/data/antviz_bio_unique.csv')
#df_sb = df.astype(str)
df_sb = df_sb.replace('indet', 'unidentified')
df_sb = df_sb.replace('(indet)', 'unidentified')
df_sb = df_sb.replace('(indet.)', 'unidentified')
df_sb.species = df_sb.species.apply(lambda x: 'unidentified' if 'indet' in x else x)
#create a df of bio and species to determine what is unique to bioregion
unique_species_df_sb = df_sb[['bioregionName','species']]
unique_species_df_sb = unique_species_df_sb.drop_duplicates(subset=['bioregionName', 'species'], keep='first')
unique_species_df_sb = unique_species_df_sb.drop('bioregionName', axis=1)
unique_species_df_sb = unique_species_df_sb.drop_duplicates(subset=['species'], keep=False)
# add column to df to indicate species uniqueness
unique_species_df_sb['bio_unique'] = 'unique'
#delete unidentified species
unique_species_df_sb=unique_species_df_sb[unique_species_df_sb.species != 'unidentified']
# join to master df to indicate species uniqueness
df_sb = pd.merge(df_sb, unique_species_df_sb, on='species', how='outer')
# delete unidentified and species not unique
df_sb = df_sb[df_sb.species != 'unidentified']
df_sb = df_sb[df_sb.species != 'NaN']
df_sb['genus'] = df_sb['genus'].str.capitalize()

def make_plot_sb(df, x_range_val_sb, bioregion_sb, genus_title):
    source_sb = df[['species', 'specimenCount']].copy()
    source_sb = source_sb.groupby('species').sum()
    hov_sb = HoverTool(tooltips=[("Species", "@species"), ("Specimens Count", "@specimenCount"), ], mode='vline')
    p_sb = figure(x_range=x_range_val_sb,
                  title=str(len(source_sb)) + ' Unique Species Found In The ' + bioregion_sb + ' Bioregion: ' + genus_title,
                  width=fig_width,
                  height=fig_height, x_axis_label="Species", y_axis_label='Specimens',
                  tools=[hov_sb, PanTool(), BoxZoomTool(), WheelZoomTool(), SaveTool(), ResetTool()])
    p_sb.vbar(x='species', width=0.9, bottom=0, top='specimenCount', color=primary_color,
              source=source_sb)
    p_sb.xaxis.major_label_orientation = x_angle
    p_sb.xgrid.grid_line_color = None
    p_sb.ygrid.grid_line_color = '#BFBFBF'
    p_sb.y_range.start = 0
    return p_sb

def update_plot_sb():
    bio_select_sb = bioselect_sb.value
    genus_select_sb = genusselect_sb.value
    if bio_select_sb == none and genus_select_sb == none:
        updated_df_sb = df_sb.copy()
        x_range_val_sb = sorted(updated_df_sb.species.unique())
        bioregion_sb = bio_select_sb
        genus_title = genus_select_sb + ' Genus Filter Applied'
    if bio_select_sb == none and genus_select_sb != none:
        updated_df_sb = df_sb[(df_sb.genus == genus_select_sb)].copy()
        x_range_val_sb = sorted(updated_df_sb.species.unique())
        bioregion_sb = bio_select_sb
        genus_title = genus_select_sb + ' Genus Filter Applied'
    if bio_select_sb != none and genus_select_sb == none:
        updated_df_sb = df_sb[(df_sb.bioregionName == bio_select_sb)].copy()
        x_range_val_sb = sorted(updated_df_sb.species.unique())
        bioregion_sb = bio_select_sb
        genus_title = genus_select_sb + ' Genus Filter Applied'
    if bio_select_sb != none and genus_select_sb != none:
        updated_df_sb = df_sb[(df_sb.bioregionName == bio_select_sb) & (df_sb.genus == genus_select_sb)].copy()
        x_range_val_sb = sorted(updated_df_sb.species.unique())
        bioregion_sb = bio_select_sb
        genus_title = genus_select_sb + ' Genus Filter Applied'
    layout_sb.children[0] = make_plot_sb(updated_df_sb, x_range_val_sb, bioregion_sb, genus_title)

# create unique species widgets
bioregion_sb = 'Afrotropical'
none = 'No Filter'
biolist_sb = sorted(df_sb['bioregionName'].unique().tolist())
bioselect_sb = Select(title="Bioregion Filter:", value=bioregion_sb, options=biolist_sb)
genuslist_sb = sorted(df_sb['genus'].unique().tolist())
genusselect_sb = Select(title="Genus Filter:", value='Parasyscia', options=genuslist_sb)

#create unique species plot
updated_df_sb = df_sb[(df_sb.bioregionName == bioregion_sb) & (df_sb.genus == 'Parasyscia')].copy()
x_range_val_sb = sorted(updated_df_sb.species.unique())
genus_title = 'Parasyscia Genus Filter Applied'
plot_sb = make_plot_sb(updated_df_sb, x_range_val_sb, bioregion_sb, genus_title)

#add unique species controls
controls_sb = [bioselect_sb, genusselect_sb]
for control_sb in controls_sb:
    control_sb.on_change('value', lambda attr, old, new: update_plot_sb())

inputs_sb = widgetbox(*controls_sb, sizing_mode=sizing_mode)

#add unique species layout
layout_sb = row(plot_sb, inputs_sb)
tab4 = Panel(child=layout_sb, title="Unique Species By Bioregion")


### Tab 5: Frequency Distribution of Specimens
df_biotaxa_species = pd.read_csv('antviz/data/antviz_biotaxa_species.csv')
df_biotaxa_species = df_biotaxa_species[['bioregionName','genus','species','specimenCount']]
df_biotaxa_species.genus = df_biotaxa_species.genus.apply(lambda x: 'unidentified' if '(' in x else x)
df_biotaxa_species.species = df_biotaxa_species.species.apply(lambda x: 'unidentified' if 'indet' in x else x)

def make_plot_freq(updated_df_freq, y_val_freq, y_label, bio_title):
    gs_bins = list(range(1,202))
    gs_labels = list(range(1,201))
    #df for frequency
    df_bins = updated_df_freq
    df_bins = df_bins.groupby(y_val_freq).sum()
    df_bins['specimenBin'] = pd.cut(df_bins.specimenCount, gs_bins, right=True, labels=gs_labels,
                                          retbins=False, include_lowest=True)
    df_bins = df_bins.groupby('specimenBin').count()
    df_bins.rename(columns={'specimenCount': 'yaxisCount'}, inplace=True)
    #create the frequency plots
    hov_freq = HoverTool(tooltips=[(y_label + " Count", "@yaxisCount"), ("Specimens", "@specimenBin"), ], mode='mouse')
    p_freq = figure(title='Frequency Distribution of Specimens By ' + y_label + ': ' + bio_title,
                  width=fig_width,
                  height=fig_height, x_axis_label="# Specimens (n)", y_axis_label='# of ' + y_label + ' with more than n specimens',
                  tools=[hov_freq, PanTool(), BoxZoomTool(), WheelZoomTool(), SaveTool(), ResetTool()]) #xrange removed
    p_freq.line('specimenBin', 'yaxisCount', line_width=2, line_color="cadetblue",
            source=df_bins)
    p_freq.circle('specimenBin', 'yaxisCount', fill_color=secondary_color, size=5, source=df_bins)
    p_freq.xaxis.major_label_orientation = x_angle
    p_freq.xgrid.grid_line_color = None
    p_freq.ygrid.grid_line_color = '#BFBFBF'
    p_freq.y_range.start = 0
    p_freq.yaxis.minor_tick_line_color = None
    return p_freq

def update_plot_freq():
    bio_select_freq = bioselect_freq.value
    yvalue_select_freq = yval_dropdown_freq.value
    if yvalue_select_freq == 'Genera' and bio_select_freq == none:
        updated_df_freq = df_biotaxa_species.copy()
        y_val_freq = 'genus'
        y_label = 'Genera'
        bio_title = 'No Bioregion Filter Applied'
    if yvalue_select_freq == 'Genera' and bio_select_freq != none:
        updated_df_freq = df_biotaxa_species[(df_biotaxa_species.bioregionName == bio_select_freq)].copy()
        y_val_freq = 'genus'
        y_label = 'Genera'
        bio_title = bio_select_freq + ' Bioregion Filter Applied'
    if yvalue_select_freq == 'Species' and bio_select_freq == none:
        updated_df_freq = df_biotaxa_species.copy()
        y_val_freq = 'species'
        y_label = 'Species'
        bio_title = 'No Bioregion Filter Applied'
    if yvalue_select_freq == 'Species' and bio_select_freq != none:
        updated_df_freq = df_biotaxa_species[(df_biotaxa_species.bioregionName == bio_select_freq)].copy()
        y_val_freq = 'species'
        y_label = 'Species'
        bio_title = bio_select_freq + ' Bioregion Filter Applied'
    layout_freq.children[0] = make_plot_freq(updated_df_freq, y_val_freq, y_label, bio_title)

# create widgets_freq
yval_dropdown_freq = Select(title="Y-Axis Dimension:", value='Genera', options=['Genera','Species'])
none = 'No Filter'
biolist_freq = sorted(df_sb['bioregionName'].unique().tolist())
biolist_freq.insert(0, none)
bioselect_freq = Select(title="Bioregion Filter:", value=none, options=biolist_freq)

# create plot_freq
y_val_freq = 'genus'
y_label = 'Genera'
bio_title = 'No Bioregion Filter Applied'
updated_df_freq = df_biotaxa_species.copy()
plot_freq = make_plot_freq(updated_df_freq, y_val_freq, y_label, bio_title)

# add controls_freq
controls_freq = [yval_dropdown_freq, bioselect_freq]
for control_freq in controls_freq:
    control_freq.on_change('value', lambda attr, old, new: update_plot_freq())

inputs_freq = widgetbox(*controls_freq, sizing_mode=sizing_mode)

#add layout_freq and style
layout_freq = row(plot_freq, inputs_freq)
tab5 = Panel(child=layout_freq, title="Frequency Distribution of Specimens By Genera/Species")


### add all tabs
tabs = Tabs(tabs=[tab1,tab2,tab3,tab4,tab5])
curdoc().add_root(tabs)
curdoc().title = "AntViz Overview"