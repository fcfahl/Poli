#!/usr/bin/env python
import os, sys, csv, shutil

from LULC_variables import *
from gdal_functions import *


def decompress_Files(year, in_Dir, in_File):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ set file name:
    if year == 2006 or year == 2012:
        in_Name = in_File + 'a.zip'
    else:
        in_Name = in_File + '.zip'

    # __________ decompress files:
    decompress_File (inDir = in_Dir, inFile = in_Name)


def reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution):

    # __________ change directory:
    os.chdir(in_Dir)

    for proj in ['3035', '3857']:

        out_Proj = 'EPSG:' + proj
        in_Clip = in_File + '.tif'
        projected = 'proj_' + proj + '_' + in_File
        out_Name =  out_Dir + out_File + '_EPSG' + proj + '.tif'
        clip_Vector = Europe[proj].inFile_Full

        #__________ set Corine projection
        set_Projection (inFile=in_Clip, inProj=in_Proj)

        #__________ reproject if needed
        if proj == '3035':
            projected = in_Clip
        else:
            reproject_File (inFile=in_Clip, outFile=projected, inProj=in_Proj, outProj=out_Proj, res=resolution, compression=compression)

        # __________ clip
        clip_File (inFile=projected, outFile=out_Name, vectorFile=clip_Vector, block=block_Size, compression=compression, noData=noData)

        # __________ overview
        gdal_ADO (inFile=out_Name, overviews=overviews)


def clean_Files(in_Dir):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ remove folder:
    shutil.rmtree(in_Dir + 'Legend', ignore_errors = True)

    # __________ list of files:
    for f in [f for f in os.listdir(".") if not f.endswith(".zip") and (f.endswith(".tif") or f.endswith(".dbf") or f.endswith(".xls") or f.endswith(".aux") or f.endswith(".tfw") or f.endswith(".doc") or f.endswith(".txt") or f.endswith(".pdf") or f.endswith(".xml") or f.endswith(".dsr"))]:

        # __________ remove files:
        print (f)
        os.remove(f)



if __name__ == "__main__":


    for year in [2012, 2006, 2000, 1990]:
#    for year in [2012]:

        index = str(year)

        in_Dir = Corine[index].inDir
        in_File = Corine[index].inFile
        out_Dir= Corine[index].outDir
        out_File= Corine[index].outFile
        in_Proj= Corine[index].projection
        noData= Corine[index].noData
        resolution= Corine[index].resolution

#        decompress_Files(year, in_Dir, in_File)
        reproject_GeoTIFF(in_Dir, in_File, out_Dir, out_File, in_Proj, noData, resolution)
#        clean_Files(in_Dir)


