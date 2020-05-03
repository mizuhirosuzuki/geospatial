import netCDF4
import csv
import numpy as np
import pandas as pd
import datetime

# Rainfall information at the time of surveys ---------------------
gis_data = pd.read_csv('../Data/GIS/gis_info_mun.csv')
chirps_annual_data = '../Data/CHIRPS/ncfile/chirps-v2.0.annual.nc'
chirps_monthly_data = '../Data/CHIRPS/ncfile/chirps-v2.0.monthly.nc'

# Convert netCDF4 files to CSV files for each municipality (from 1981 to 2019 = 39 years)
precipitation_output = pd.DataFrame()

for i in gis_data['inegi_code']:
    municipality = gis_data[gis_data['inegi_code'] == i]
    chirps = netCDF4.Dataset(chirps_annual_data)
    lon = np.array(chirps.variables['longitude'][:])
    lat = np.array(chirps.variables['latitude'][:])
    
    # Find grids surrounding the municipality
    lon_near_argsort = np.argsort(abs(lon - np.array(municipality['lon'])))
    lon_near1 = lon_near_argsort[0]
    lon_near2 = lon_near_argsort[1]
    lat_near_argsort = np.argsort(abs(lat - np.array(municipality['lat'])))
    lat_near1 = lat_near_argsort[0]
    lat_near2 = lat_near_argsort[1]
    
    # Calculate distances from the municipality centroid to each grid
    surrounding_grid1_dist = np.sqrt((lon[lon_near1] - municipality['lon']) ** 2 + (lat[lat_near1] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid2_dist = np.sqrt((lon[lon_near1] - municipality['lon']) ** 2 + (lat[lat_near2] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid3_dist = np.sqrt((lon[lon_near2] - municipality['lon']) ** 2 + (lat[lat_near1] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid4_dist = np.sqrt((lon[lon_near2] - municipality['lon']) ** 2 + (lat[lat_near2] - municipality['lat']) ** 2).iloc[0]
    
    precip1 = np.array(chirps['precip'][:,lat_near1,lon_near1])
    precip1[precip1 == -9999] = np.nan
    precip2 = np.array(chirps['precip'][:,lat_near1,lon_near2])
    precip2[precip2 == -9999] = np.nan
    precip3 = np.array(chirps['precip'][:,lat_near2,lon_near1])
    precip3[precip3 == -9999] = np.nan
    precip4 = np.array(chirps['precip'][:,lat_near2,lon_near2])
    precip4[precip4 == -9999] = np.nan
    
    try:
        numerator = 0
        denominator = 0
        for precip, dist in zip([precip1, precip2, precip3, precip4], [surrounding_grid1_dist, surrounding_grid2_dist, surrounding_grid3_dist, surrounding_grid4_dist]):
            if ~np.isnan(precip).any():
                numerator += precip / dist
                denominator += 1 / dist
        chirps_precip = numerator / denominator
    except:
        chirps_precip = np.empty_like(precip1)
        chirps_precip[:] = np.nan

    precipitation_output_temp = pd.DataFrame(chirps_precip).transpose()
    precipitation_output_temp['inegi_code'] = municipality['inegi_code'].iloc[0]
    precipitation_output = pd.concat([precipitation_output, precipitation_output_temp])

colnames = []
for year in range(1981, 2020):
    colnames.append("precip_" + str(year))
colnames.append('inegi_code')
precipitation_output.columns = colnames

precipitation_output.to_csv('../Data/CHIRPS/annual_precip.csv')

# Convert netCDF4 files to CSV files for each municipality (monthly)
precipitation_output = pd.DataFrame()

for i in gis_data['inegi_code']:
    municipality = gis_data[gis_data['inegi_code'] == i]
    chirps = netCDF4.Dataset(chirps_monthly_data)
    lon = np.array(chirps.variables['longitude'][:])
    lat = np.array(chirps.variables['latitude'][:])
    
    # Find grids surrounding the municipality
    lon_near_argsort = np.argsort(abs(lon - np.array(municipality['lon'])))
    lon_near1 = lon_near_argsort[0]
    lon_near2 = lon_near_argsort[1]
    lat_near_argsort = np.argsort(abs(lat - np.array(municipality['lat'])))
    lat_near1 = lat_near_argsort[0]
    lat_near2 = lat_near_argsort[1]
    
    # Calculate distances from the municipality centroid to each grid
    surrounding_grid1_dist = np.sqrt((lon[lon_near1] - municipality['lon']) ** 2 + (lat[lat_near1] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid2_dist = np.sqrt((lon[lon_near1] - municipality['lon']) ** 2 + (lat[lat_near2] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid3_dist = np.sqrt((lon[lon_near2] - municipality['lon']) ** 2 + (lat[lat_near1] - municipality['lat']) ** 2).iloc[0]
    surrounding_grid4_dist = np.sqrt((lon[lon_near2] - municipality['lon']) ** 2 + (lat[lat_near2] - municipality['lat']) ** 2).iloc[0]
    
    precip1 = np.array(chirps['precip'][:,lat_near1,lon_near1])
    precip1[precip1 == -9999] = np.nan
    precip2 = np.array(chirps['precip'][:,lat_near1,lon_near2])
    precip2[precip2 == -9999] = np.nan
    precip3 = np.array(chirps['precip'][:,lat_near2,lon_near1])
    precip3[precip3 == -9999] = np.nan
    precip4 = np.array(chirps['precip'][:,lat_near2,lon_near2])
    precip4[precip4 == -9999] = np.nan
    
    try:
        numerator = 0
        denominator = 0
        for precip, dist in zip([precip1, precip2, precip3, precip4], [surrounding_grid1_dist, surrounding_grid2_dist, surrounding_grid3_dist, surrounding_grid4_dist]):
            if ~np.isnan(precip).any():
                numerator += precip / dist
                denominator += 1 / dist
        chirps_precip = numerator / denominator
    except:
        chirps_precip = np.empty_like(precip1)
        chirps_precip[:] = np.nan
    
    precipitation_output_temp = pd.DataFrame(chirps_precip).transpose()
    precipitation_output_temp['inegi_code'] = municipality['inegi_code'].iloc[0]
    precipitation_output = pd.concat([precipitation_output, precipitation_output_temp])

colnames = []
for year in range(1981, 2020):
    for month in range(1, 13):
        colnames.append("precip_" + str(year) + "_" + str(month))
colnames.append("precip_2020_" + str(1))
colnames.append('inegi_code')
precipitation_output.columns = colnames

precipitation_output.to_csv('../Data/CHIRPS/monthly_precip.csv')

goopy

# Rainfall information at 12 years old --------------------------
gis_data = pd.read_csv('../Data/GIS/gis_info_state_12.csv')
chirps_annual_data = '../Data/CHIRPS/ncfile/chirps-v2.0.annual.nc'
chirps_monthly_data = '../Data/CHIRPS/ncfile/chirps-v2.0.monthly.nc'

# Convert netCDF4 files to CSV files for each municipality (from 1981/1 to 2018/7 = 451 months)
precipitation_output = pd.DataFrame()

for i in gis_data['state_12']:
    state = gis_data[gis_data['state_12'] == i]
    chirps = netCDF4.Dataset(chirps_monthly_data)
    lon = np.array(chirps.variables['longitude'][:])
    lat = np.array(chirps.variables['latitude'][:])
    
    # Find grids surrounding the state
    lon_near_argsort = np.argsort(abs(lon - np.array(state['lon'])))
    lon_near1 = lon_near_argsort[0]
    lon_near2 = lon_near_argsort[1]
    lat_near_argsort = np.argsort(abs(lat - np.array(state['lat'])))
    lat_near1 = lat_near_argsort[0]
    lat_near2 = lat_near_argsort[1]

    # Calculate distances from the state centroid to each grid
    surrounding_grid1_dist = np.sqrt((lon[lon_near1] - state['lon']) ** 2 + (lat[lat_near1] - state['lat']) ** 2).iloc[0]
    surrounding_grid2_dist = np.sqrt((lon[lon_near1] - state['lon']) ** 2 + (lat[lat_near2] - state['lat']) ** 2).iloc[0]
    surrounding_grid3_dist = np.sqrt((lon[lon_near2] - state['lon']) ** 2 + (lat[lat_near1] - state['lat']) ** 2).iloc[0]
    surrounding_grid4_dist = np.sqrt((lon[lon_near2] - state['lon']) ** 2 + (lat[lat_near2] - state['lat']) ** 2).iloc[0]
    
    precip1 = np.array(chirps['precip'][:,lat_near1,lon_near1])
    precip2 = np.array(chirps['precip'][:,lat_near1,lon_near2])
    precip3 = np.array(chirps['precip'][:,lat_near2,lon_near1])
    precip4 = np.array(chirps['precip'][:,lat_near2,lon_near2])
    
    chirps_precip = (
                    precip1 * (1 / surrounding_grid1_dist) + 
                    precip2 * (1 / surrounding_grid1_dist) + 
                    precip3 * (1 / surrounding_grid1_dist) + 
                    precip4 * (1 / surrounding_grid1_dist)
                    ) / ((1 / surrounding_grid1_dist) +  (1 / surrounding_grid1_dist) +  (1 / surrounding_grid1_dist) +  (1 / surrounding_grid1_dist))

    precipitation_output_temp = pd.DataFrame(chirps_precip).transpose()
    precipitation_output_temp['state_12'] = state['state_12']
    precipitation_output = pd.concat([precipitation_output, precipitation_output_temp])

colnames = []
for year in range(1981, 2018):
    for month in range(1, 13):
        colnames.append("precip_" + str(year) + "_" + str(month))
for month in range(1, 8):
    colnames.append("precip_2018_" + str(month))
colnames.append('state_12')

precipitation_output.columns = colnames
output.to_csv('../Data/CHIRPS/monthly_precip_12.csv')

goopy

# ----------------------------------------- #
# Zero rain and its spell

def maxConsecutive(input): 
    # input.split('0') --> splits all sub-strings of consecutive 1's 
    # separated by 0's, output will be like ['11','1111','1','1','111'] 
    # map(len,input.split('0'))  --> map function maps len function on each  
    # sub-string of consecutive 1's 
    # max() returns maximum element from a list 
    return max(map(len,input.split('0')))

gis_data = pd.read_csv('../Data/GIS/gis_info_man.csv')

chirps_data_list = ['../../data/CHIRPS/Daily/chirps-v2.0.1981.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1982.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1983.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1984.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1985.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1986.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1987.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1988.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1989.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1990.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1991.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1992.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1993.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1994.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1995.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1996.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1997.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1998.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.1999.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2000.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2001.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2001.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2002.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2003.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2004.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2005.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2006.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2007.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2008.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2009.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2010.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2011.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2012.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2013.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2014.days_p05.nc',
                    '../../data/CHIRPS/Daily/chirps-v2.0.2015.days_p05.nc']

## Convert netCDF4 files to CSV files for each municipality (from 1981 to 2015)
#for i in gis_data['inegi_code']:
#    municipality = gis_data[gis_data['inegi_code'] == i]
#    time_var_output = np.array([])
#    precipitation_output = np.array([])
#    for chirps_data in chirps_data_list:
#        chirps = netCDF4.Dataset(chirps_data)
#        time_var = netCDF4.num2date(chirps.variables['time'][:], chirps.variables['time'].units)
#        lon = np.array(chirps.variables['longitude'][:])
#        lat = np.array(chirps.variables['latitude'][:])
#        
#        lon_near_index = np.argmin(abs(lon - np.array(municipality['lon'])))
#        lat_near_index = np.argmin(abs(lat - np.array(municipality['lat'])))
#        chirps_municipality = np.array(chirps['precip'][:,lat_near_index,lon_near_index])
#
#        time_var_output = np.append(time_var_output, time_var)
#        precipitation_output = np.append(precipitation_output, chirps_municipality)
#
#    output = pd.DataFrame()
#    output['date'] = time_var_output
#    output['precipitation'] = precipitation_output
#
#    save_path = '../Data/CHIRPS/Daily/' + str(i) + '.csv'
#    output.to_csv(save_path)

# Create average precipitation during field work
precipitation_output = np.empty((0, 35 * 2 + 1), int)

for i in gis_data['inegi_code']:
    municipality = gis_data[gis_data['inegi_code'] == i]

    climate_data = pd.read_csv('../Data/CHIRPS/Daily/'+str(int(i))+'.csv')
    climate_data_time_var = climate_data['date']
    climate_data_time_var_split = climate_data_time_var.str.split('-', expand=True)

    test = np.array([datetime.datetime(climate_data_time_var_split.loc[[t],0],climate_data_time_var_split.loc[[t],1],climate_data_time_var_split.loc[[t],2]) for t in climate_data_time_var_split.index])

    zero_rain_list_year = []
    zero_rain_spell_list_year = []
    for year in range(1981, 2016):
        climate_data_year = climate_data[(test > datetime.datetime(year, 1, 1)) & (test <= datetime.datetime(year, 12, 31))]

        zero_rain_list_year.append((climate_data_year['precipitation'] < .1).sum())
        zero_rain_spell_list_year.append(maxConsecutive(''.join(str(e) for e in list((climate_data_year['precipitation'] < .1) * 1))))

    precipitation_output = np.vstack((precipitation_output, np.concatenate((np.array(municipality['inegi_code']), zero_rain_list_year, zero_rain_spell_list_year))))

colnames = ['inegi_code']
for year in range(1981, 2016):
    colnames.append("zero_rain_" + str(year))
for year in range(1981, 2016):
    colnames.append("zero_rain_spell_" + str(year))

output = pd.DataFrame(precipitation_output, columns = colnames)
output.to_csv('../Data/CHIRPS/daily_precip.csv')

## Rainfall information at 12 years old --------------------------
gis_data = pd.read_csv('../Data/GIS/gis_info_state_12.csv')

## Convert netCDF4 files to CSV files for each municipality (from 1981 to 2015)
#for i in gis_data['state_12']:
#    municipality = gis_data[gis_data['state_12'] == i]
#    time_var_output = np.array([])
#    precipitation_output = np.array([])
#    for chirps_data in chirps_data_list:
#        chirps = netCDF4.Dataset(chirps_data)
#        time_var = netCDF4.num2date(chirps.variables['time'][:], chirps.variables['time'].units)
#        lon = np.array(chirps.variables['longitude'][:])
#        lat = np.array(chirps.variables['latitude'][:])
#        
#        lon_near_index = np.argmin(abs(lon - np.array(municipality['lon'])))
#        lat_near_index = np.argmin(abs(lat - np.array(municipality['lat'])))
#        chirps_municipality = np.array(chirps['precip'][:,lat_near_index,lon_near_index])
#
#        time_var_output = np.append(time_var_output, time_var)
#        precipitation_output = np.append(precipitation_output, chirps_municipality)
#
#    output = pd.DataFrame()
#    output['date'] = time_var_output
#    output['precipitation'] = precipitation_output
#
#    save_path = '../Data/CHIRPS/Daily/' + str(i) + '_12.csv'
#    output.to_csv(save_path)

# Create average precipitation during field work
precipitation_output = np.empty((0, 35 * 2 + 1), int)

for i in gis_data['state_12']:
    municipality = gis_data[gis_data['state_12'] == i]

    climate_data = pd.read_csv('../Data/CHIRPS/Daily/'+str(int(i))+'_12.csv')
    climate_data_time_var = climate_data['date']
    climate_data_time_var_split = climate_data_time_var.str.split('-', expand=True)

    test = np.array([datetime.datetime(climate_data_time_var_split.loc[[t],0],climate_data_time_var_split.loc[[t],1],climate_data_time_var_split.loc[[t],2]) for t in climate_data_time_var_split.index])

    zero_rain_list_year = []
    zero_rain_spell_list_year = []
    for year in range(1981, 2016):
        climate_data_year = climate_data[(test > datetime.datetime(year, 1, 1)) & (test <= datetime.datetime(year, 12, 31))]

        zero_rain_list_year.append((climate_data_year['precipitation'] < .1).sum())
        zero_rain_spell_list_year.append(maxConsecutive(''.join(str(e) for e in list((climate_data_year['precipitation'] < .1) * 1))))

    precipitation_output = np.vstack((precipitation_output, np.concatenate((np.array(municipality['state_12']), zero_rain_list_year, zero_rain_spell_list_year))))

colnames = ['state_12']
for year in range(1981, 2016):
    colnames.append("zero_rain_" + str(year))
for year in range(1981, 2016):
    colnames.append("zero_rain_spell_" + str(year))

output = pd.DataFrame(precipitation_output, columns = colnames)
output.to_csv('../Data/CHIRPS/daily_precip_12.csv')

    




