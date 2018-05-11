import requests
import pandas as pd

# basemap data from Ken Alger/Treehouse: https://teamtreehouse.com/library/data-visualization-with-bokeh
#url_map = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
#r_map =  requests.get(url_map)

### data for Species Density choropleth map
geolocales_url = "http://api.antweb.org/v3/geolocales?georank=country"
r_geolocales = requests.get(geolocales_url)
geolocales_data = r_geolocales.json()
geolocales_raw_df = pd.DataFrame.from_dict(geolocales_data['geolocales'])
## create csv for choropleth map
geolocales_raw_df.to_csv('antviz_choropleth.csv')


### data for Specimens Overview
#specimens_1980_url = 'http://api.antweb.org/v3/specimens?maxDate=1979-12-31&limit=100000'
#r_specimens_1980 = requests.get(specimens_1980_url)
#specimens1980_data = r_specimens_1980.json()
#specimens1980_df = pd.DataFrame.from_dict(specimens1980_data['specimens'])
#specimens1980_df = specimens1980_df[['dateCollected', 'country', 'subfamily','biogeographicregion','ownedby', 'collectedby', 'code']]
#specimens1980_df.to_csv('specimens1980.csv')

#specimens_1980_2000_url = 'http://api.antweb.org/v3/specimens?minDate=1980-01-01&maxDate=1999-12-31&limit=500000'
#r_specimens_1980_2000 = requests.get(specimens_1980_2000_url)
#specimens1980_2000_data = r_specimens_1980_2000.json()
#specimens1980_2000_df = pd.DataFrame.from_dict(specimens1980_2000_data['specimens'])
#specimens1980_2000_df = specimens1980_2000_df[['dateCollected', 'country', 'subfamily','biogeographicregion','ownedby', 'collectedby', 'code']]
#specimens1980_2000_df.to_csv('specimens1980_2000.csv')

#specimens_2000_2005_url = 'http://api.antweb.org/v3/specimens?minDate=2000-01-01&maxDate=2005-12-31&limit=800000'
#r_specimens_2000_2005 = requests.get(specimens_2000_2005_url)
#specimens2000_2005_data = r_specimens_2000_2005.json()
#specimens2000_2005_df = pd.DataFrame.from_dict(specimens2000_2005_data['specimens'])
#specimens2000_2005_df = specimens2000_2005_df[['dateCollected', 'country', 'subfamily','biogeographicregion','ownedby', 'collectedby', 'code']]
#specimens2000_2005_df.to_csv('specimens2000_2005.csv')

#specimens_2006_2010_url = 'http://api.antweb.org/v3/specimens?minDate=2006-01-01&maxDate=2010-12-31&limit=800000'
#r_specimens_2006_2010 = requests.get(specimens_2006_2010_url)
#specimens2006_2010_data = r_specimens_2006_2010.json()
#specimens2006_2010_df = pd.DataFrame.from_dict(specimens2006_2010_data['specimens'])
#specimens2006_2010_df = specimens2006_2010_df[['dateCollected', 'country', 'subfamily','biogeographicregion','ownedby', 'collectedby', 'code']]
#specimens2006_2010_df.to_csv('specimens2006_2010.csv')

specimens_2011_2018_url = 'http://api.antweb.org/v3/specimens?minDate=2011-01-01&maxDate=2018-12-31&limit=800000'
r_specimens_2011_2018 = requests.get(specimens_2011_2018_url)
specimens2011_2018_data = r_specimens_2011_2018.json()
specimens2011_2018_df = pd.DataFrame.from_dict(specimens2011_2018_data['specimens'])
specimens2011_2018_df = specimens2011_2018_df[['dateCollected', 'country', 'subfamily','biogeographicregion','ownedby', 'collectedby', 'code']]
specimens2011_2018_df.to_csv('specimens2011_2018.csv')

### create a single file with all specimens
df1 = pd.read_csv('specimens1980.csv', error_bad_lines=False)
df2 = pd.read_csv('specimens1980_2000.csv', error_bad_lines=False)
df3 = pd.read_csv('specimens2000_2005.csv', error_bad_lines=False)
df4 = pd.read_csv('specimens2006_2010.csv', error_bad_lines=False)
df5 = pd.read_csv('specimens2011_2018.csv', error_bad_lines=False)
df_all = pd.concat([df2, df3, df4, df5])
df_all.to_csv('specimens_all.csv')


### data for Bioregion Overview
url_bio = "http://api.antweb.org/v3/bioregions"
r_bio = requests.get(url_bio)
data_bio = r_bio.json()
df_bio = pd.DataFrame.from_dict(data_bio['bioregions'])
df_bio.to_csv('antviz_species_by_bioregion.csv')


### data for Unique Species By Bioregion
url_species_bioregion = "http://api.antweb.org/v3/bioregionTaxa?rank=species&limit=500000"
r_species_bioregion = requests.get(url_species_bioregion)
data_species_bioregion = r_species_bioregion.json()
df_sb = pd.DataFrame.from_dict(data_species_bioregion['bioregionTaxa'])
df_sb.to_csv('antviz_bio_unique.csv')


### data for Frequency Distribution of Specimens By Genera/Species
url_biotaxa_species = "http://api.antweb.org/v3/bioregionTaxa?rank=species&limit=500000"
r_biotaxa_species = requests.get(url_biotaxa_species)
data_biotaxa_spececies = r_biotaxa_species.json()
df_biotaxa_species = pd.DataFrame.from_dict(data_biotaxa_spececies['bioregionTaxa'])
df_biotaxa_species.to_csv('antviz_biotaxa_species.csv')
