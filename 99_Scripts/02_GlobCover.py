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
    
    # __________ decompress files:
    decompress_File (inDir = in_Dir, inFile = in_File)
    
  
def fix_GeoTIFF(in_Dir, in_File): 
    
#==============================================================================
#     https://grasswiki.osgeo.org/wiki/Global_datasets#ESA_Globcover_dataset
#==============================================================================

    # __________ change directory:
    os.chdir(in_Dir)
    
    # __________ reproject and clip files:        
    fixed = 'fixed_' + in_File      
    
    # __________ fix geotiff boundaries 
    fix_Geotiff_Boundaries (inFile=in_File, outFile=fixed, BBOX='-180 90 180 -65')    
    

def reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):  
        
    # __________ change directory:
    os.chdir(in_Dir)
    
    # __________ clip BBOX   
    clip_BBOX = Europe['BBOX_4326'].inFile_Full
    in_Clip = 'clip_' + in_File    

    clip_File (inFile=in_File, outFile=in_Clip, vectorFile=clip_BBOX, block='', compression=compression, noData=noData)

    
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
    for f in [f for f in os.listdir(".") if not f.endswith(".zip") and (f.endswith(".tif") or f.endswith(".dbf") or f.endswith(".xls") or f.endswith(".avl") or f.endswith(".dsl") or f.endswith(".lyr") or f.endswith(".jpg") or f.endswith(".pdf") or f.endswith(".xml") or f.endswith(".dsr"))]:
    
        # __________ remove files:        
        print (f)
        os.remove(f)
        
        

if __name__ == "__main__":     
    

    for year in [2005, 2009]:
        
        index = str(year)
        
        in_Dir = GlobCover[index].inDir         
        in_File = GlobCover[index].inFile 
        out_Dir= GlobCover[index].outDir 
        out_File= GlobCover[index].outFile
        in_Proj= GlobCover[index].projection    
        noData= GlobCover[index].noData    
        resolution= GlobCover[index].resolution      
        
        
        # __________ reproject and clip files: 
        if year == 2005:
            in_Zip = 'Globcover_V2.2_Global.zip'        
            
        elif year == 2009:
            in_Zip = 'Globcover2009_V2.3_Global_.zip'        
        


#        decompress_Files(in_Dir, in_File=in_Zip)
        reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)
#        clean_Files(in_Dir)
