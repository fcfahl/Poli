#!/usr/bin/env python
import os, sys, urllib2, csv
import pandas as pd
from cookielib import CookieJar
from urllib import urlencode

from LULC_variables import *
from gdal_functions import *



def create_Folders(first_Year, last_Year):

    for year in xrange(first_Year, last_Year, 1):    
    
        index = 'MODIS_' + str(year) 

        in_MODIS =  MODIS[index].inDir
        out_MODIS =  MODIS[index].outDir

        # __________ create if it not exist
        if not os.path.exists(in_MODIS):
            os.makedirs(in_MODIS)
            
        if not os.path.exists(out_MODIS):
            os.makedirs(out_MODIS)

        # __________ change directory:
        os.chdir(in_MODIS)


def get_Granules(first_Year, last_Year):

    in_CSV = MODIS['MODIS_2001'].inSource + MODIS['MODIS_2001'].inFile

    # __________ red CSV with MODIS granules
    df = pd.read_csv(in_CSV)

    # __________ delete columns
    df = df.drop('Browse_URLs', 1)
    df = df.drop('Cloud_Cover', 1)
    df = df.drop('Day_Night', 1)
    df = df.drop('Size', 1)
    df = df.drop('Granule', 1)
    

    # __________ extract year data
    df['Year'] = df['Start'].map(lambda x: str(x)[:-16])

    # __________ export CSV
    for year in xrange(first_Year, last_Year, 1):
        
        index = 'MODIS_' + str(year) 
   
        out_File = MODIS[index].inFile
        out_Dir = MODIS[index].inDir

         # __________ change directory:
        os.chdir(out_Dir)

        # __________ select data
        df2 = df[df['Year'] == str(year)]

        # __________ export csv
        df2.to_csv(out_File, sep=',', header=True, index=False, columns=['URLs'])
        

def download_MODIS(first_Year, last_Year):
    
    #==============================================================================
    #    https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
    #==============================================================================
    
          
    # __________ Earthdata Login  
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", "fahl0514", "Rosana40")    
     
    # __________ Create a cookie jar for storing cookies.          
    cookie_jar = CookieJar()
    
    # __________ install all the handlers.         
    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        urllib2.HTTPCookieProcessor(cookie_jar))
    
    urllib2.install_opener(opener) 
   
    for year in xrange(first_Year, last_Year, 1):
        
        
        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile   
        
        # __________ change directory:
        os.chdir(in_Dir)

        # __________ read CSV
        df = pd.read_csv(in_File)
        
        # __________ convert datafrane to list
        row_list = df.to_csv(None, header=False, index=False, skip=0).split('\n') 

        # __________ set variables
        MODIS[index].list_TMP = ['name']
       
        for url in row_list: 
            
            if url <> '':
                
                #__________ set output file name                 
                tile = (url.strip().split('/')[-1]).split('.')[2]              
                out_File = str(year) + '_' + tile    
                
 
                #__________ Create and submit the request         
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)  

                #__________ write output file   
                with open(out_File + '.hdf' ,'wb') as output:
                    output.write(response.read())                  

                #__________ append output file names to a tmp variable            
                MODIS[index].list_TMP.append( out_File )             

                      
        # __________ export file names               
        out_CSV = open(index + '.csv', 'wb')
        wr = csv.writer(out_CSV, delimiter='\n')

        wr.writerow(MODIS[index].list_TMP)


def convert_GeoTIFF(first_Year, last_Year):
    
    for year in xrange(first_Year, last_Year, 1):
        
        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        
        # __________ change directory:
        os.chdir(in_Dir)
        
        # __________ read CSV
        df = pd.read_csv(index + '.csv')  
        
        # __________ convert datafrane to list
        row_list = df.to_csv(None, header=False, index=False).split('\n') 

        
        for HDF in row_list: 
            
            if HDF[5:] <> '':
#            if HDF[5:] == 'h20v02':                
                
                for type_LULC in [1,2,3,4,5]:
                    
                    in_HDF = 'HDF4_EOS:EOS_GRID:' + HDF + '.hdf:MOD12Q1:Land_Cover_Type_' + str(type_LULC)
                    out_GeoTIFF = HDF + '_LCType_' + str(type_LULC) + '.tif'
            
                    gdal_Translate(inFile=in_HDF, outFile=out_GeoTIFF, format='GTiff')
                    
        
  
def merge_GeoTIFF(first_Year, last_Year):   
    
    for year in xrange(first_Year, last_Year, 1):
        
        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        
        # __________ change directory:
        os.chdir(in_Dir)
        
        # __________ read CSV
        df = pd.read_csv(index + '.csv')        
        
                
        for type_LULC in [1,2,3,4,5]:
            
            
            suffix  =  'LCType_' + str(type_LULC)            
            
            df['tiffs'] = df + '_' + suffix + '.tif'  

            # __________ convert datafrane to list
            geotiff_list = (' '.join(df['tiffs'].to_csv(None, header=False, index=False).split('\n')))[:-1]

            inFile =   geotiff_list 
            
            gdal_Merge (inFile=inFile, outFile=suffix + '.tif')
            
            
            
def reproject_GeoTIFF(first_Year, last_Year):   
    
    for year in xrange(first_Year, last_Year, 1):  

        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        out_Dir= MODIS[index].outDir 
        out_File= MODIS[index].outFileFull 
        
        # __________ change directory:
        os.chdir(in_Dir)
        
        clip_Vector = Europe['3857'].inFile_Full
        
        in_Proj = '\'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs\''
        out_Proj = 'EPSG:3857'
        
         # __________ reproject and clip files:       
        for type_LULC in [1,2,3,4,5]:            
            
            original  =  'LCType_' + str(type_LULC) + '.tif' 
            projected  =   out_File + '_Type' + str(type_LULC) + '_EPSG3857.tif'
             
            reproject_File (inFile=original, outFile=projected, vectorFile=clip_Vector, inProj=in_Proj, outProj=out_Proj)

        # __________ delete tif files:
        filelist = [ f for f in os.listdir(".") if f.endswith(".tif") or f.endswith(".vrt") or f.endswith(".xml")  ]
        for f in filelist:
            os.remove(f)
            
def clip_GeoTIFF(first_Year, last_Year):   
    
    for year in xrange(first_Year, last_Year, 1):  
            
            
            
def add_Colortable(first_Year, last_Year):   
    
    for year in xrange(first_Year, last_Year, 1):
        
        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        out_Dir= MODIS[index].outDir 
        out_File= MODIS[index].outFile
        
        # __________ change directory:
        os.chdir(out_Dir)
        
                 # __________ reproject and clip files:       
        for type_LULC in [1,2,3,4,5]:
   
            file_Name  =   out_File + '_Type' + str(type_LULC) + '_EPSG3857.tif'
            
            print LULC_Colors['MODIS'].inFile_Full
            
            gdal_Add_Color (inFile=file_Name, colorTable=LULC_Colors['MODIS'].inFile_Full, categories=LULC_Cats['MODIS'].inFile_Full)
            

def add_Overview (first_Year, last_Year):   
    
    for year in xrange(first_Year, last_Year, 1):
        
        index = 'MODIS_' + str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        out_Dir= MODIS[index].outDir 
        out_File= MODIS[index].outFile
        
        # __________ change directory:
        os.chdir(out_Dir)
        
                 # __________ reproject and clip files:       
#        for type_LULC in [1,2,3,4,5]:
        for type_LULC in [5]:
#        
            file_Name  =   out_File + '_Type' + str(type_LULC) + '_EPSG3857.tif'
            
            gdal_ADO (inFile=file_Name, overviews='2 4 8 16 32 64' )

            
        

if __name__ == "__main__":
    
    first_Year = 2001
#    last_Year = 2013
    last_Year = 2002

#    create_Folders(first_Year, last_Year)
#    get_Granules(first_Year, last_Year)
#    download_MODIS(first_Year, last_Year)
#    convert_GeoTIFF(first_Year, last_Year)
#    merge_GeoTIFF(first_Year, last_Year)
    reproject_GeoTIFF(first_Year, last_Year)
#    clip_GeoTIFF(first_Year, last_Year)
#    add_Colortable(first_Year, last_Year)
#    add_Overview(first_Year, last_Year)



#
