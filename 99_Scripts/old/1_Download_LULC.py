#!/usr/bin/env python
import os, sys, csv
import pandas as pd
import datetime as DT
import LULC_variables

tiles_MODIS = ['h15v03','h15v05','h16v01','h16v02','h16v05','h16v06','h17v01','h17v02','h17v03','h17v04','h17v05','h17v06','h18v01','h18v02','h18v03','h18v04','h18v05','h18v06','h19v01','h19v02','h19v03','h19v04','h19v05','h19v06','h20v01','h20v02','h20v03','h20v04','h20v05','h20v06','h21v03','h21v04','h21v05','h21v06','h22v05','h22v06']

http_Base = 'http://reverb.echo.nasa.gov/reverb/url_hashes/28vs4e6y'

http_Files = []


def create_Folders():

    for year in xrange(2001, 2013, 1):
#    for year in xrange(2001, 2002, 1):

        in_MODIS = 'MODIS_' + str(year) + '.inDir'
        exec("%s=%s" %("in_MODIS",in_MODIS))

        # __________ create if it not exist
        if not os.path.exists(in_MODIS):
            os.makedirs(in_MODIS)

        # __________ change directory:
        os.chdir(in_MODIS)



def get_Granules():

    in_CSV = MODIS_2001.inSource + MODIS_2001.inFile


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


    # __________ export data
    for year in xrange(2001, 2013, 1):

        
        key = 'MODIS_' + str(year) 
   
        out_File = MODIS[key].inFile
        out_Dir = MODIS[key].inDir

         # __________ change directory:
        os.chdir(out_Dir)

        # __________ select data
        df2 = df[df['Year'] == str(year)]

        # __________ export csv
        df2.to_csv(out_File, sep=',', header=False, index=False, columns=['URLs'])




#create_Folders()
get_Granules()
#download_MODIS()

