#!/usr/bin/env python
import os, sys, urllib2, csv
import pandas as pd
from cookielib import CookieJar
from urllib import urlencode

from LULC_variables import *
from gdal_functions import *   

    
def create_Folders(in_Dir, out_Dir):

    # __________ create folder if it does not exist
    if not os.path.exists(in_Dir):
        os.makedirs(in_Dir)
        
    if not os.path.exists(out_Dir):
        os.makedirs(out_Dir)


def get_Granules(in_Dir, in_File, df, year):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ select data
    df2 = df[df['Year'] == str(year)]

    # __________ export csv
    df2.to_csv(in_File, sep=',', header=True, index=False, columns=['URLs'])
    
    
def download_MODIS(index, in_Dir, in_File):
    
    #==============================================================================
    #    https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
    #==============================================================================     
      
    # __________ change directory:
    os.chdir(in_Dir)

    # __________ read CSV
    df = pd.read_csv(in_File)
    
    # __________ convert datafrane to list
    row_list = df.to_csv(None, header=False, index=False, skip=0).split('\n') 

    # __________ set variables
    MODIS[index].list_TMP = ['name']
   
    for url in row_list:        
        
#        if url.endswith('h20v02.051.2014287163637.hdf'):  
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
    
def decompress_Files(in_Dir):  
    
#==============================================================================
#     in case the hdf files are compacted
#==============================================================================
        
    # __________ change directory:
    os.chdir(in_Dir)        
    
    # __________ list of files:   
    for f in [f for f in os.listdir(".") if f.endswith(".zip")]:
    
        # __________ decompress files:
        try:
            decompress_File (inDir = in_Dir, inFile = f)
        except:
            pass
    
    
def convert_GeoTIFF(year, in_Dir, in_File, noData, resolution):    
        
    # __________ change directory:
    os.chdir(in_Dir)
    
    # __________ read CSV for each year
    df = pd.read_csv('MODIS_' + year + '.csv')  
    
    # __________ convert datafrane to list
    row_list = df.to_csv(None, header=False, index=False).split('\n') 

    
    for HDF in row_list: 
        
        if HDF[5:] <> '':
#        if HDF[5:] == 'h20v02':                
            
            for type_LULC in [1,2,3,4,5]:
                
                in_HDF = 'HDF4_EOS:EOS_GRID:' + HDF + '.hdf:MOD12Q1:Land_Cover_Type_' + str(type_LULC)
                out_GeoTIFF = HDF + '_LCType_' + str(type_LULC) + '.tif'
        
                gdal_Translate(inFile=in_HDF, outFile=out_GeoTIFF, format='GTiff', noData=noData, compression='')

    
def merge_GeoTIFF(year, in_Dir, in_File, noData, resolution): 
       
    # __________ change directory:
    os.chdir(in_Dir)
    
    # __________ read CSV for each year
    df = pd.read_csv('MODIS_' + year + '.csv')  
    
            
    for type_LULC in [1,2,3,4,5]:        
        
        suffix  =  'LCType_' + str(type_LULC)            
        
        df['tiffs'] = df + '_' + suffix + '.tif'  

        # __________ convert datafrane to list
        geotiff_list = (' '.join(df['tiffs'].to_csv(None, header=False, index=False).split('\n')))[:-1]

        inFile = geotiff_list 
        
        gdal_Merge (inFile=inFile, outFile=suffix + '.tif', noData=noData, compression=compression)    
    

def reproject_GeoTIFF(year, in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):  
        
    # __________ change directory:
    os.chdir(in_Dir)
    
    for proj in ['3035', '3857']:
    
         # __________ reproject and clip files:       
        for type_LULC in [1,2,3,4,5]:
            
                        
            in_Name = 'LCType_' + str(type_LULC) + '.tif'
            projected = 'proj_' + in_Name
            
            out_Proj = 'EPSG:' + proj            
            projected = 'proj_' + proj + '_' + in_Name            
            
            out_Name =  out_Dir + out_File + '_Type' + str(type_LULC) + '_EPSG' + proj + '.tif'
            clip_Vector = Europe[proj].inFile_Full               

    
            # __________ reproject:          
            reproject_File (inFile=in_Name , outFile=projected, inProj=in_Proj, outProj=out_Proj, res=resolution, compression=compression)
    
            # __________ clip
            clip_File (inFile=projected, outFile=out_Name, vectorFile=clip_Vector, block=block_Size, compression=compression, noData=noData)
    
            # __________ overview
            gdal_ADO (inFile=out_Name, overviews=overviews)
    



def clean_Files(in_Dir):  
        
    # __________ change directory:
    os.chdir(in_Dir)

    # __________ delete tif files:
    filelist = [ f for f in os.listdir(".") if f.endswith(".tif") or f.endswith(".vrt") or f.endswith(".xml")  ]
    
    for f in filelist:
        print 'remove file -> %s' % (f)
        os.remove(f)


def compact_Files(in_Dir):  
        
    # __________ change directory:
    os.chdir(in_Dir)    
    
    # __________ list of files:   
    for f in [f for f in os.listdir(".") if f.endswith(".hdf")]:
    
        # __________ compact hdf files:
#        compress_File (inFile = f)

        # __________ remove hdf files:        
        os.remove(f)
        
        


if __name__ == "__main__": 

    # __________ red CSV with MODIS granules
    in_CSV = MODIS['2001'].inSource + MODIS['2001'].inFile
    df = pd.read_csv(in_CSV)

    # __________ delete columns
    df = df.drop('Browse_URLs', 1)
    df = df.drop('Cloud_Cover', 1)
    df = df.drop('Day_Night', 1)
    df = df.drop('Size', 1)
    df = df.drop('Granule', 1)    

    # __________ extract year data
    df['Year'] = df['Start'].map(lambda x: str(x)[:-16])    
 
          
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

    
    # __________ time range    
    first_Year = 2001
    last_Year = 2013
#    last_Year = 2002        
    
    for year in xrange(first_Year, last_Year, 1):
        
        index = str(year)
        
        in_Dir = MODIS[index].inDir         
        in_File = MODIS[index].inFile 
        out_Dir= MODIS[index].outDir 
        out_File= MODIS[index].outFile    
        in_Proj= MODIS[index].projection    
        noData= MODIS[index].noData    
        resolution= MODIS[index].resolution      

#        create_Folders(in_Dir, out_Dir)
#        get_Granules(in_Dir, in_File, df, year)
#        download_MODIS(index, in_Dir, in_File)
#        decompress_Files(in_Dir)
#        convert_GeoTIFF(index, in_Dir, in_File, noData, resolution)
#        merge_GeoTIFF(index, in_Dir, in_File, noData, resolution)
        reproject_GeoTIFF(index, in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)
#        clean_Files(in_Dir)
#        compact_Files(in_Dir)
