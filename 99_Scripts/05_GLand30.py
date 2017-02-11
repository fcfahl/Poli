#!/usr/bin/env python
import os, sys, csv, shutil
import pandas as pd

from LULC_variables import *
from gdal_functions import *


def decompress_Files(year, df, zones, in_Dir, in_File):

    # __________ change directory:
    os.chdir(in_Dir)


    for zone in zones:

        zone_DIR = in_Dir + 'Zone_' + str(zone)

        # __________  create folder for each zone
        if not os.path.exists(zone_DIR):
            os.makedirs(zone_DIR)

        # __________  get sheet names
        sheets = df[(df['Zone']==zone)]['Sheet']

        for sheet in sheets:

            sheet_Name = sheet + '_' + str(year) + 'LC030'

            # __________ decompress files:
            decompress_File (inDir = zone_DIR , inFile = in_Dir + '/Original/' + sheet_Name + '.zip')

            # __________ move geotiff files
            for ext in ['.tif', '.tfw']:
                geotiff = sheet_Name.lower() + ext

                in_Path = zone_DIR + '/' + sheet_Name + '/' + geotiff
                out_Path = zone_DIR + '/' + geotiff

                if os.path.exists(in_Path):
                    shutil.move(in_Path, out_Path)

            # __________ remove directory:
            shutil.rmtree(zone_DIR + '/' + sheet_Name)



def reproject_Zones(year, df, zones, in_Dir, in_File, noData, in_Proj, resolution):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ set general variables
    zone_Files = {'3035':'','3857':''}
    zone_List_3035 = []
    zone_List_3857 = []

    for zone in zones:

        print zone

        zone_DIR = in_Dir + 'Zone_' + str(zone)
        merge_UTM = 'Zone_' + str(zone) + '_' + str(year)
        sheet_List = []

        # __________ change directory:
        os.chdir(zone_DIR)

        # __________  get sheet names
        sheets = df[(df['Zone']==zone)]['Sheet']

        for sheet in sheets:

            sheet_Name = str(sheet.lower() + '_' + str(year) + 'lc030.tif')

            sheet_List.append (sheet_Name)

        files = " ".join(sheet_List)

        # __________  merge zones
        gdal_Merge (inFile=files, outFile=merge_UTM + '.tif', noData=noData, compression=compression)

        # __________  reproject zones

        for proj in ['3035', '3857']:

            in_Proj = 'EPSG:326' + str(zone)
            out_Proj = 'EPSG:' + proj
            in_Name = merge_UTM + '.tif'
            projected = '_'.join(['proj', proj, in_Name])
            out_Name = '/'.join([zone_DIR, projected])

            if proj == '3035':
                zone_List_3035.append (out_Name)
                zone_Files[proj] = " ".join(zone_List_3035)

            else:
                zone_List_3857.append (out_Name)
                zone_Files[proj] = " ".join(zone_List_3857)

            # __________  reproject zones
            reproject_File (inFile=in_Name, outFile=projected, inProj=in_Proj, outProj=out_Proj, res=resolution, compression=compression)


def merge_Zones(in_Dir, in_File, out_Dir, noData):

    # __________ change directory:
    os.chdir(in_Dir)

    # __________ set general variables
    zone_Files = {'3035':'','3857':''}

    for proj in ['3857']:
#    for proj in ['3035', '3857']:

        in_Proj = 'EPSG:' + proj

        files = zone_Files[proj]
        out_Name =  out_File + '_EPSG' + proj + '.tif'
        TMP_Name = '_'.join(['TMP', out_Name])
        clip_Vector = Europe[proj].inFile_Full


        # __________  merge zones
#        gdal_Merge (inFile=files, outFile=TMP_Name, noData=noData, compression=compression)

        # __________ clip
        clip_File (inFile=TMP_Name, outFile=out_Dir + out_Name, vectorFile=clip_Vector, block=block_Size, compression=compression, noData=noData)


def retile_Geotiff (in_File, out_Dir):

    # __________ change directory:
    os.chdir(out_Dir)

    # __________ set general variables
    zone_Files = {'3035':'','3857':''}

    for proj in ['3857']:
#    for proj in ['3035', '3857']:

        # __________ change directory:
        final_Dir = out_Dir + 'EPSG' + str(proj)
        os.chdir(final_Dir)

        in_Proj = 'EPSG:' + proj

        files = zone_Files[proj]
        file_Name = out_File + '_EPSG' + proj
        in_Name = out_Dir + '_'.join(['GLand30_EPSG', str(proj)]) + '.tif'
        out_Name =  out_Dir + out_File + '_EPSG' + proj + '.tif'


        print file_Name
        print out_Name

        # __________  merge zones
        gdal_Tile (inFile=out_Name, out_Folder=final_Dir, in_Proj=in_Proj, dim_Tiles=tiles_Size, out_Vector=file_Name + '.shp', out_CSV=file_Name + '.csv', levels=10)




if __name__ == "__main__":


    for year in [2010]:

        index = str(year)

        in_Dir = GLand30[index].inDir
        in_File = GLand30[index].inFile
        out_Dir = GLand30[index].outDir
        out_File = GLand30[index].outFile
        in_Proj = GLand30[index].projection
        noData = GLand30[index].noData
        resolution = GLand30[index].resolution

        # __________ read CSV
        df = pd.read_csv(in_Dir + in_File)

        # __________ get UTM Zones
        zones = df['Zone'].unique().tolist()


#        decompress_Files(year, df, zones, in_Dir, in_File )
#        reproject_Zones(year, df, zones, in_Dir, in_File, noData, in_Proj, resolution)
#        merge_Zones(in_Dir, in_File, out_Dir, noData)
        retile_Geotiff(in_File, out_Dir)


#        clean_Files(in_Dir)

