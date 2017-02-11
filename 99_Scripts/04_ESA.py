#!/usr/bin/env python
import os, sys, urllib2, csv, shutil
import pandas as pd
from cookielib import CookieJar
from urllib import urlencode

from LULC_variables import *
from gdal_functions import *  


def decompress_Files(in_Dir, in_File):  
        
    # __________ change directory:
    os.chdir(in_Dir)    
    
    print in_File + '.7z'
    
    # __________ decompress files: 
    decompress_7z (inZip = in_File + '.7z', inFile = in_File)
    
  
def fix_GeoTIFF(in_Dir, in_File): 
    
    #==============================================================================
    #     https://grasswiki.osgeo.org/wiki/Global_datasets#ESA_Globcover_dataset
    #==============================================================================

    # __________ change directory:
    os.chdir(in_Dir)
    
    # __________ fix geotiff boundaries 
    fixed = 'fixed_' + in_File    
    fix_Geotiff_Boundaries (inFile=in_File, outFile=fixed, BBOX='-180 90 180 -90', compression=compression)
#    

def reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):  

    # __________ change directory:
    os.chdir(in_Dir)
        
    # __________ clip BBOX
    fixed = 'fixed_' + in_File    
    clip_BBOX = Europe['BBOX_4326'].inFile_Full
    in_Clip = 'clip_' + in_File    

    clip_File (inFile=fixed, outFile=in_Clip, vectorFile=clip_BBOX, block='', compression=compression, noData=noData)

    
    for proj in ['3035', '3857']:

        out_Proj = 'EPSG:' + proj
        projected = 'proj_' + proj + '_' + in_File
        out_Name =  out_Dir + out_File + '_EPSG' + proj + '.tif'
        clip_Vector = Europe[proj].inFile_Full

        #__________ reproject:
        reproject_File (inFile=in_Clip, outFile=projected, inProj=in_Proj, outProj=out_Proj, res=resolution, compression=compression)

        # __________ clip
        clip_File (inFile=projected, outFile=out_Name, vectorFile=clip_Vector, block=block_Size, compression=compression, noData=noData)

        # __________ overview
        gdal_ADO (inFile=out_Name, overviews=overviews)
        
        
def clean_Files(in_Dir):  
    
    # __________ change directory:
    os.chdir(in_Dir)    
        
    # __________ list of files:   
    for f in [f for f in os.listdir(".") if not f.endswith(".7z") and (f.endswith(".tif"))]:
    
        # __________ remove hdf files:        
        print (f)
#        os.remove(f)
        
        

if __name__ == "__main__":       
     
    
    for year in [2005, 2010]:
#    for year in [2000, 2005, 2010]:
        
        index = str(year)
        
        in_Dir = ESA[index].inDir         
        in_File = ESA[index].inFile 
        out_Dir= ESA[index].outDir 
        out_File= ESA[index].outFile   
        in_Proj= ESA[index].projection    
        noData= ESA[index].noData    
        resolution= ESA[index].resolution      
                
        
        


#        decompress_Files(in_Dir, in_File)
        fix_GeoTIFF(in_Dir, in_File)
        reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)
#        clean_Files(in_Dir)
