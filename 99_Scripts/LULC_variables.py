#!/usr/bin/env python
import os, sys

#_________Check OS
if sys.platform.startswith('linux'):
    home = os.getenv("HOME") + '/Poli/'
elif sys.platform.startswith('win'):
#    home = 'E:/TEMP/99_Linux/'
    home = 'C:/data/Poli/'
else:
    raise OSError('Platform not configured.')

#_________data location
data_Source =  home + '02_Data_Sources/'
data_Process =  home + '03_Data_Processing/'
data_GRASS =  home + '04_GRASS_Database/'
data_Script =  home + '99_Scripts/'
data_LULC =  '02_LULC/'
data_Color =  data_Process + '99_Color_Rules/'


MODIS_script_generator = 'https://lpdaac.usgs.gov/data_access/daac2disk'
Modis_LULC_parameter = 'MCD12Q1'


class Files:

    def getName(self):
        return self.__class__.__name__

    def __init__(self, ID, inFile, nameFile, outFile, mapset, inDir, outDir, *parameter):

        self.ID = ID
        self.inFile = inFile
        self.name = self.ID + '_' + nameFile
        self.nameAt = self.name  + '@' + mapset
        self.outFile = outFile
        self.mapset = mapset
        self.inDir = inDir
        self.outDir = outDir
        self.inFile_Full = inDir + inFile
        self.outFile_Full = outDir + outFile

        self.parameter = parameter


#_________Set LULC classes
class LULC:

    def getName(self):
        return self.__class__.__name__

    def __init__(self, LULC, year, inFile, resolution, noData, projection):

        number = {
          'GLC':'01',
          'GlobCover':'02',
          'MODIS':'03',
          'ESA':'04',
          'GLand30':'05',
          'Corine':'06',
          'GHSL':'07',
        }
        source = {
          'GLC':'http://forobs.jrc.ec.europa.eu/products/glc2000/products.php',
          'GlobCover':'http://due.esrin.esa.int/page_globcover.php',
          'MODIS':'https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mcd12q1',
          'ESA':'http://maps.elie.ucl.ac.be/CCI/viewer/download.php',
          'GLand30':'http://www.globallandcover.com/GLC30Download/index.aspx',
          'Corine':'http://land.copernicus.eu/pan-european/corine-land-cover',
          'GHSL':'http://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GPW4_GLOBE_R2015A/',
        }

        name = number[LULC] + '_' + LULC

        self.source = source[LULC]
        self.inSource = data_Source + data_LULC + name +'/'
        self.inProcess = data_Process + data_LULC + name +'/'

        self.inDir = self.inSource + str(year) + '/'
        self.inFile = inFile
        self.inFileFull = self.inDir + inFile

        self.outDir = self.inProcess + str(year) + '/'
        self.outFile = LULC + '_' + year
        self.outFileFull = self.outDir + self.outFile

        self.resolution = resolution
        self.noData = noData
        self.projection = projection
        
        self.color = data_Color + LULC + "_Color.txt"
        self.cats = data_Color + LULC + "_Cats.txt"

        self.list_TMP = [] # variable to hold temporary lists

#==============================================================================
#                                      Variables
#==============================================================================

block_Size = '256'
tiles_Size = '2048'
overviews='2 4 8 16 32 64'
compression = 'LZW'
#    compression = 'NONE'

#==============================================================================
#                                      General files
#==============================================================================

#_________ Vector files
Europe = {
    '3035':Files('L01', 'Europe_EPSG3035.shp', 'Europe_EPSG3035', '', '', data_Source + '01_ADM/EPSG_3035/', ''),
    '3857':Files('L02', 'Europe_EPSG3857.shp', 'Europe_EPSG3857', '', '', data_Source + '01_ADM/EPSG_3857/', ''),
    '4326':Files('L03', 'Europe_EPSG4326.shp', 'Europe_EPSG4326', '', '', data_Source + '01_ADM/EPSG_4326/', ''),
    'BBOX_4326':Files('L04', 'BBOX_EPSG4326.shp', 'BBOX_EPSG4326', '', '', data_Source + '01_ADM/EPSG_4326/', ''),
    'BBOX_54009':Files('L05', 'BBOX_EPSG54009.shp', 'BBOX_EPSG54009', '', '', data_Source + '01_ADM/EPSG_54009/', ''),
    }


Countries = {
    '3035':Files('L01', 'NUTS_Countries_EPSG3035_dis.shp', 'Countries_EPSG3035', '', '', data_Source + '01_ADM/EPSG_3035/', ''),
    '3857':Files('L02', 'NUTS_Countries_EPSG3857.shp', 'Countries_EPSG3857', '', '', data_Source + '01_ADM/EPSG_3857/', ''),
    '4326':Files('L03', 'NUTS_Countries_EPSG4326.shp', 'Countries_EPSG4326', '', '', data_Source + '01_ADM/EPSG_4326/', ''),
    }

#_________ Color definition files

LULC_Colors = {
    'GLC_2000':Files('C01', 'GLC2000_Color.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'GlobCover':Files('C02', 'GlobCover_Color.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'MODIS':Files('C03', 'MODIS_Color.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'ESA':Files('C04', 'ESA_Color.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'Corine':Files('C05', 'ESA_Color.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    }

LULC_Cats = {
    'GLC_2000':Files('C01', 'GLC2000_Cats.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'GlobCover':Files('C02', 'GlobCover_Cats.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'MODIS':Files('C03', 'MODIS_Cats.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'ESA':Files('C04', 'ESA_Cats.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    'Corine':Files('C05', 'ESA_Cats.txt', '', '', '',data_Process + '99_Color_Rules/', '', ''),
    }

#==============================================================================
#                                      LULC datasets
#==============================================================================

#_________ GLC variable instances
GLC_2000 = {
    '2000':LULC('GLC', '2000', 'GLC_EU_V2.bil', 1000, '0', 'EPSG:4326'),
    }

#_________ GlobCover variable instances
GlobCover = {
    '2005':LULC('GlobCover', '2005', 'GLOBCOVER_200412_200606_V2.2_Global_CLA.tif', 300, '255', 'EPSG:4326'),
    '2009':LULC('GlobCover', '2009', 'GLOBCOVER_L4_200901_200912_V2.3.tif', 300, '255', 'EPSG:4326'),
    }

#_________ MODIS variable instances
sinusoidal = '\'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs\''

MODIS = {
    '2001':LULC('MODIS', '2001', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2002':LULC('MODIS', '2002', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2003':LULC('MODIS', '2003', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2004':LULC('MODIS', '2004', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2005':LULC('MODIS', '2005', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2006':LULC('MODIS', '2006', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2007':LULC('MODIS', '2007', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2008':LULC('MODIS', '2008', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2009':LULC('MODIS', '2009', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2010':LULC('MODIS', '2010', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2011':LULC('MODIS', '2011', 'MODIS_granule.csv', 500, '255', sinusoidal),
    '2012':LULC('MODIS', '2012', 'MODIS_granule.csv', 500, '255', sinusoidal),
    }

#_________ ESA variable instances
ESA = {
    '2000':LULC('ESA', '2000', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2000-v1.6.1.tif', 300, '255', 'EPSG:4326'),
    '2005':LULC('ESA', '2005', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.tif', 300, '255', 'EPSG:4326'),
    '2010':LULC('ESA', '2010', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2010-v1.6.1.tif', 300, '255', 'EPSG:4326'),
    }

#_________ GLand30 variable instances
GLand30 ={
    '2000':LULC('GLand30', '2000', 'Zones_Sheets.csv', 30, '0', 'EPSG:326'),
    '2010':LULC('GLand30', '2010', 'Zones_Sheets.csv', 30, '0', 'EPSG:326'),
    }

#_________ Corine variable instances
Corine = {
    '1990':LULC('Corine', '1990', 'g100_clc90_V18_5', 100, '255', 'EPSG:3035'),
    '2000':LULC('Corine', '2000', 'g100_clc00_V18_5', 100, '255', 'EPSG:3035'),
    '2006':LULC('Corine', '2006', 'g100_clc06_V18_5', 100, '255', 'EPSG:3035'),
    '2012':LULC('Corine', '2012', 'g100_clc12_V18_5', 100, '255', 'EPSG:3035'),
    }


#_________ GHSL variable instances
GHSL = {
    '1975':LULC('GHSL', '1975', 'GHS_POP_GPW41975_GLOBE_R2015A_54009_250_v1_0', 250, '0', 'EPSG:54009'),
    '1990':LULC('GHSL', '1990', 'GHS_POP_GPW41990_GLOBE_R2015A_54009_250_v1_0', 250, '0', 'EPSG:54009'),
    '2000':LULC('GHSL', '2000', 'GHS_POP_GPW42000_GLOBE_R2015A_54009_250_v1_0', 250, '0', 'EPSG:54009'),
    '2015':LULC('GHSL', '2015', 'GHS_POP_GPW42015_GLOBE_R2015A_54009_250_v1_0', 250, '0', 'EPSG:54009'),
    }

