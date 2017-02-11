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
  
    

def reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):  
        
    # __________ change directory:
    os.chdir(in_Dir + 'Binary/')
    
    for proj in ['3035', '3857']:

        out_Proj = 'EPSG:' + proj
        in_Clip = in_File
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
        
    # __________ remove directory:
    shutil.rmtree(in_Dir)
        
        

if __name__ == "__main__": 

  
    in_Dir = GLC_2000['2000'].inDir         
    in_File = GLC_2000['2000'].inFile 
    out_Dir= GLC_2000['2000'].outDir 
    out_File= GLC_2000['2000'].outFile    
    in_Proj= GLC_2000['2000'].projection    
    noData= GLC_2000['2000'].noData    
    resolution= GLC_2000['2000'].resolution    


    decompress_Files(in_Dir, in_File='EUv2_Binary.zip')
    reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)
    clean_Files(in_Dir + 'Binary/')

