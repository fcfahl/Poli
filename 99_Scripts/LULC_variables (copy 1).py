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
    
#_________Set folders
    
class folder_Definition:
    
    def __init__(self, name, number):
        
        nameFull = number + '_' + name
        
        self.inSource = data_Source + data_LULC + nameFull +'/'
        self.inProcess = data_Process + data_LULC + nameFull +'/'
        
 
#_________Set LULC classes
 
class LULC:

    def __init__(self, LULC, year, inFile):      

        source = {
          'GLC': '',
          'GlobCover': '',
          'MODIS': '',
          'ESA': 'http://maps.elie.ucl.ac.be/CCI/viewer/download.php',
          'GLand30': '',
          'Corine': 'http://land.copernicus.eu/pan-european/corine-land-cover'
        }[LULC]
       
        self.source = source
        self.inDir = folder_ESA.inSource + str(year) + '/'
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile 


 
class GLC:
    
    def __init__(self, year, inFile):
        
        self.source = ''
        self.inDir = folder_GLC.inSource + str(year)  
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile
        
class GlobCover:
    
    def __init__(self, year, inFile):
        
        self.source = ''
        self.inDir = folder_GlobCover.inSource + str(year)  
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile  
        
class MODIS:
    
    def __init__(self, year, inFile):
        
        self.source = ''
        self.inDir = folder_MODIS.inSource + str(year)    
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile  
        
class ESA:
    
    def __init__(self, year, inFile):	
        
        self.source = 'http://maps.elie.ucl.ac.be/CCI/viewer/download.php'
        self.inDir = folder_ESA.inSource + str(year) + '/'
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile  

  
class GLand30:
    
    def __init__(self, year, inFile):
        
        self.source = ''
        self.inDir = folder_GLand30.inSource + str(year)   
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile  
  
class Corine:
    
    def __init__(self, year, inFile):
        
        self.source = 'http://land.copernicus.eu/pan-european/corine-land-cover'
        self.inDir = folder_Corine.inSource + str(year)   
        self.inFile = inFile  
        self.inFileFull = self.inDir + inFile          

#_________ Create folder instances

folder_GLC = folder_Definition('GLC', '01')
folder_GlobCover = folder_Definition('GlobCover', '02')
folder_MODIS = folder_Definition('MODIS', '03')
folder_ESA = folder_Definition('ESA', '04')
folder_GLand30 = folder_Definition('GLand30', '05')
folder_Corine = folder_Definition('Corine', '06')

#_________ GLC variable instances
GLC_2000 = LULC('GLC', '2000', 'FIle')

#_________ GlobCover variable instances
GlobCover_2000 = LULC('GlobCover', '2000', 'FIle')
GlobCover_2005 = LULC('GlobCover', '2005', 'FIle')
GlobCover_2010 = LULC('GlobCover', '2010', 'FIle')

#_________ MODIS variable instances
MODIS_2002 = LULC('MODIS', '2002', 'FIle')
MODIS_2003 = LULC('MODIS', '2003', 'FIle')
MODIS_2004 = LULC('MODIS', '2004', 'FIle')
MODIS_2005 = LULC('MODIS', '2005', 'FIle')
MODIS_2006 = LULC('MODIS', '2006', 'FIle')
MODIS_2007 = LULC('MODIS', '2007', 'FIle')
MODIS_2008 = LULC('MODIS', '2008', 'FIle')
MODIS_2009 = LULC('MODIS', '2009', 'FIle')
MODIS_2010 = LULC('MODIS', '2010', 'FIle')
MODIS_2011 = LULC('MODIS', '2011', 'FIle')
MODIS_2012 = LULC('MODIS', '2012', 'FIle')

#_________ ESA variable instances
ESA_2000 = LULC('ESA', '2000', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2000-v1.6.1.tif.7z')
ESA_2005 = LULC('ESA', '2005', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.tif.7z')
ESA_2010 = LULC('ESA', '2010', 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2010-v1.6.1.tif.7z')

#_________ GLand30 variable instances
GLand30_2000 = LULC('GLand30', '2000', 'FIle')
GLand30_2010 = LULC('GLand30', '2010', 'FIle')

#_________ Corine variable instances
Corine_2000 = LULC('Corine', '2000', 'FIle')
Corine_2005 = LULC('Corine', '2005', 'FIle')
Corine_2010 = LULC('Corine', '2010', 'FIle')


#==============================================================================
# a = ESA()
# b = a.year_2000('test')
# 
# print b.source2
#==============================================================================
