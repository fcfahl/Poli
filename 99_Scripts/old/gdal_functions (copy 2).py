import os, sys, ogr, osr
from osgeo import gdal
from shutil import copyfile


import zipfile


def message (text, filename):
    print "\n________________________\n%s -> %s \n" % (text, filename)

#==============================================================================
#                           Compress Function
#                   Source: https://pymotw.com/2/zipfile/ 
#==============================================================================



def decompress_File (inDir, inFile):

    with zipfile.ZipFile(inFile, "r") as z:
        z.extractall(inDir)
    
    
    
def compress_File (inFile):
    
    outFile = inFile + '.zip'

    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    
    modes = { zipfile.ZIP_DEFLATED: 'deflated',
              zipfile.ZIP_STORED:   'stored',
              }              
              
    message ('creating archive ', inFile)
    
    zf = zipfile.ZipFile(outFile, mode='w')
    
    try:
        print 'compression mode %s' % (modes[compression])
        zf.write(inFile, compress_type=compression)
    finally:
        zf.close()


#==============================================================================
#                               GDAL functions
#==============================================================================

# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()



def raster_metadata (inFile):
    message ('metadata ', inFile)
    try:
        src_ds = gdal.Open(inFile)
        print src_ds.GetMetadata()
        
        
    except RuntimeError, e:
        message ('unable to open ', inFile)
        print e
        sys.exit(1) 
  
def add_Tiles (inFile, outFile, block): 

    message ('add_Tiles ', inFile)    

    os.system('gdal_translate -co BIGTIFF=YES -co TILED=YES -co BLOCKXSIZE=%s -co BLOCKYSIZE=%s -co compress=LZW %s %s ' %(block, block, inFile, outFile)) 
  
    
def clip_File (inFile, outFile, vectorFile, block, compression='', noData='-9999'):

    message ('clip_File ', inFile)  
    
    os.system('gdalwarp -overwrite --config GDAL_CACHEMAX 500 -wm 500 -wo NUM_THREADS=ALL_CPUS -co TILED=YES -co BLOCKXSIZE=%s -co BLOCKYSIZE=%s -co compress=%s -dstnodata %s -crop_to_cutline -cutline %s %s %s ' %(block, block, compression, noData, vectorFile, inFile, outFile)) 
        
        
def reproject_File (inFile, outFile, inProj, outProj):   
    
    message ('reproject_File ', inFile)  

    os.system('gdalwarp -overwrite --config GDAL_CACHEMAX 500 -wm 500 -wo NUM_THREADS=ALL_CPUS -co BIGTIFF=YES -s_srs %s -t_srs %s -of GTiff %s %s ' %(inProj, outProj, inFile, outFile))
       
        
def convert_Geotiff (inProj, inFile, outFile):    
    
    message ('convert_Geotiff ', inFile)  

    tmp2File = 'tmp_' + outFile
    
    try:        
        # convert to Geotiff
        os.system('gdal_translate -of "GTiff" %s %s ' %(inFile, tmp2File))
        os.system('gdalwarp -t_srs %s %s %s' %(inProj, tmp2File, outFile))
        os.remove(tmp2File)        
        message ('converting file', outFile)
        
    except:
        message ('unable to convert file', inFile)
        pass


def gdal_Translate (inFile, outFile, format):
    
    message ('gdal_translate ', inFile)  
    
    os.system('gdal_translate -of "%s" %s %s ' %(format, inFile, outFile))
 
 
def gdal_Merge (inFile, outFile):
    
    message ('gdal_Merge ', inFile)      
    
    vrt = outFile + '.vrt'
    
    os.system('gdalbuildvrt %s %s ' % (vrt, inFile))    
    gdal_Translate(inFile=vrt, outFile=outFile, format='GTiff')


def gdal_Add_Color (inFile, colorTable, categories):

    message ('gdal_Add_Color ', inFile)  
    
    tmp_File = inFile + '.tmp'  
    
    copyfile(inFile,tmp_File)   
    os.remove(inFile)    
    
    vrt = inFile + '.vrt'    
    vrt2 = inFile + '_2.vrt'    
   
    
    # __________ read colortable (grass format) and create a xml template    
    color_xml = '\t<ColorInterp>Palette</ColorInterp>\n\t<ColorTable>\n'  
     
    fp = open(colorTable, "r")
    for line in fp:
        if line.find('#') == -1 and line.find('/') == -1:
            entry = line.replace(':',' ').split()
            if len(entry) == 5:
                alpha = int(entry[4])
            else:
                alpha=0
            
            if entry:
                value =  entry [0]
                c1 =  entry [1]
                c2 =  entry [2]
                c3 =  entry [3]
                color_xml += '\t\t<%s c1="%s" c2="%s" c3="%s" c4="%s"/>\n' % (value, c1, c2, c3, alpha)
            
    fp.close()

    color_xml +='\t</ColorTable>\n'
    
    # __________ read category (grass format) and create a xml template      
    cat_xml = '\t<CategoryNames>\n'  
     
    fp = open(categories, "r")
    for line in fp:
        if line.find('#') == -1 and line.find('/') == -1:
            entry = line.strip().split('|')
            value =  entry [0]
            description =  entry [1]
            cat_xml += '\t\t<Category>%s</Category>\n' % (description)
           
    fp.close()

    cat_xml +='\t</CategoryNames>\n'    
    
    
    # __________ create a vrt file
    os.system('gdal_translate -of "VRT" %s %s ' %(tmp_File, vrt))
    
    
    # __________ replace xml palette on vrt file 
    f1 = open(vrt, 'r')
    f2 = open(vrt2, 'w')
    for line in f1:
        if line.strip().startswith('<ColorInterp>'):
            f2.write(color_xml)
            f2.write(cat_xml)
        elif line.strip().startswith('<Entry c1=') or line.strip().endswith('ColorTable>') :
            f2.write('')
        else:
            f2.write(line)
    f1.close()
    f2.close()    
    

    # __________ convert  vrt to geotiff file    
    os.system('gdal_translate -of "GTiff" %s %s ' %(vrt2, inFile))
    
    # __________ remove tmp file
    os.remove(tmp_File)
    os.remove(vrt)
    os.remove(vrt2)

               
def gdal_ADO (inFile, overviews):    
    
    message ('gdaladdo ', inFile)      
    
    os.system('gdaladdo -r average %s %s ' %(inFile, overviews)) 


def gdal_Tile (inFile, out_Folder, in_Proj, dim_Tiles, out_Vector, out_CSV, levels=10):

    message ('gdal_retile ', inFile)  
    
    os.system('gdal_retile -s_srs %s -v -r bilinear -useDirForEachRow -levels %s -ps %s %s -co "TILED=YES" -co "BLOCKXSIZE=256"  -co "BLOCKYSIZE=256" -co "COMPRESS=LZW"  -tileIndex %s -csv %s -targetDir %s %s ' %(in_Proj, levels, dim_Tiles, dim_Tiles, out_Vector, out_CSV, out_Folder, inFile)) 
    