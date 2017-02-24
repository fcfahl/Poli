#!/usr/bin/env python
import os, sys, csv, shutil

from LULC_variables import *
from gdal_functions import *


def decompress_Files(in_Dir, in_File):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ decompress files:
    decompress_File (inDir = in_Dir, inFile = in_File + '.zip')
    
    
    # __________ change directory:
    os.chdir(in_Dir + in_File)

    # __________ list of files:
    for f in [f for f in os.listdir(".") if not f.endswith(".zip") and (f.endswith(".pdf") or f.endswith(".aux.xml") or f.endswith(".tif.xml") or  f.endswith(".ovr") )]:

        # __________ remove files:
        print (f)
        os.remove(f)    


def reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):

    # __________ change directory:
    os.chdir(in_Dir + in_File )

    # __________ set general variables
    in_Name = in_File + '.tif'
    in_Clip = 'clip_' + in_Name

    clip_BBOX= Europe['BBOX_54009'].inFile_Full
    
    in_Proj_D = "'+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs'"

    # __________ clip BBOX
    clip_File (inFile=in_Name, outFile=in_Clip, vectorFile=clip_BBOX, block='', compression=compression, noData=noData)


    for proj in ['3035', '3857']:

        out_Proj = 'EPSG:' + proj
        projected = 'proj_' + proj + '_' + in_Name
        out_Name =  in_Dir + out_File + '_EPSG' + proj + '.tif'
        clip_Vector = Europe[proj].inFile_Full

        #__________ reproject:
        reproject_File (inFile=in_Clip, outFile=projected, inProj=in_Proj_D, outProj=out_Proj, res=resolution, compression=compression)

        # __________ clip
        clip_File (inFile=projected, outFile=out_Name, vectorFile=clip_Vector, block=block_Size, compression=compression, noData=noData)

        # __________ overview
        gdal_ADO (inFile=out_Name, overviews=overviews)


    # __________ remove folder:
    shutil.rmtree(in_Dir + in_File, ignore_errors = True)


if __name__ == "__main__":


#    for year in [2015, 2000, 1990, 1975]:
    for year in [2015]:

        index =  str(year)

        in_Dir = GHSL[index].inDir
        in_File = GHSL[index].inFile
        out_Dir= GHSL[index].outDir
        out_File= GHSL[index].outFile
        in_Proj= GHSL[index].projection
        noData= GHSL[index].noData
        resolution= GHSL[index].resolution

#        decompress_Files(in_Dir, in_File )
        reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)



