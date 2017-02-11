#!/usr/bin/env python
import os, sys

#_________Check OS
if sys.platform.startswith('linux'):
    home = os.getenv("HOME") + '/GIS/'
    data_Source =  home + '02_Data_Sources/'    
    data_Process =  home + '03_Data_Processing/'    
    data_GRASS =  home + '04_GRASS_Database/'    
    data_Script =  home + '99_Scripts/'    
    data_LULC =  '02_LULC/'   

    
elif sys.platform.startswith('win'):
    home = 'C:/'
    data_Source ='C:/'
    
else:
    raise OSError('Platform not configured.')  
    
    
MODIS_script_generator = 'https://lpdaac.usgs.gov/data_access/daac2disk'
Modis_LULC_parameter = 'MCD12Q1'
 
#_________Set LULC classes 
class LULC:

    def __init__(self, LULC, year, inFile):      

        number = {
          'GLC':'01',
          'GlobCover':'02',
          'MODIS':'03',
          'ESA':'04',
          'GLand30':'05',
          'Corine':'06'
        }
        source = {
          'GLC':'http://forobs.jrc.ec.europa.eu/products/glc2000/products.php',
          'GlobCover':'http://due.esrin.esa.int/page_globcover.php',
          'MODIS':'https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mcd12q1',
          'ESA':'http://maps.elie.ucl.ac.be/CCI/viewer/download.php',
          'GLand30':'http://www.globallandcover.com/GLC30Download/index.aspx',
          'Corine':'http://land.copernicus.eu/pan-european/corine-land-cover'
        }
        
        name = number[LULC] + '_' + LULC
       
        self.source = source[LULC]
        self.inSource = data_Source + data_LULC + name +'/'
        self.inProcess = data_Process + data_LULC + name +'/'
        
        self.inDir = self.inSource + str(year) + '/'
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile 


#_________ GLC variable instances
GLC_2000 = LULC('GLC', '2000', 'EUv2_Binary.zip')

#_________ GlobCover variable instances
GlobCover_2005 = LULC('GlobCover', '2005', 'Globcover_V2.2_Global.zip')
GlobCover_2009 = LULC('GlobCover', '2009', 'FIle')

#_________ MODIS variable instances

MODIS = {
    'MODIS_2001':LULC('MODIS', '2001', 'MODIS_granule.csv'),
    'MODIS_2002':LULC('MODIS', '2002', 'MODIS_granule.csv'),
    'MODIS_2003':LULC('MODIS', '2003', 'MODIS_granule.csv'),
    'MODIS_2004':LULC('MODIS', '2004', 'MODIS_granule.csv'),
    'MODIS_2005':LULC('MODIS', '2005', 'MODIS_granule.csv'),
    'MODIS_2006':LULC('MODIS', '2006', 'MODIS_granule.csv'),
    'MODIS_2007':LULC('MODIS', '2007', 'MODIS_granule.csv'),
    'MODIS_2008':LULC('MODIS', '2008', 'MODIS_granule.csv'),
    'MODIS_2009':LULC('MODIS', '2009', 'MODIS_granule.csv'),
    'MODIS_2010':LULC('MODIS', '2010', 'MODIS_granule.csv'),
    'MODIS_2011':LULC('MODIS', '2011', 'MODIS_granule.csv'),
    'MODIS_2012':LULC('MODIS', '2012', 'MODIS_granule.csv')    
    }

#_________ ESA variable instances
ESA_2000 = LULC('ESA', '2000', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2000-v1.6.1.tif.7z')
ESA_2005 = LULC('ESA', '2005', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.tif.7z')
ESA_2010 = LULC('ESA', '2010', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2010-v1.6.1.tif.7z')

#_________ GLand30 variable instances
GLand30_2000 = LULC('GLand30', '2000', 'FIle')
GLand30_2010 = LULC('GLand30', '2010', 'FIle')

#_________ Corine variable instances
Corine_1990 = LULC('Corine', '1990', 'g100_clc90_V18_5.zip')
Corine_2000 = LULC('Corine', '2000', 'g100_clc00_V18_5.zip')
Corine_2005 = LULC('Corine', '2005', 'g100_clc06_V18_5a.zip')
Corine_2010 = LULC('Corine', '2010', 'g100_clc12_V18_5a.zip')


