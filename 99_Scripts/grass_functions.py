import grass.script as grass
import variables as var
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d
from grass.pygrass.modules import Module
import grass.pygrass as py
import grass.pygrass.gis.region as re
import grass.pygrass.vector as vector
import grass.pygrass.vector.table as table
import grass.pygrass.vector.geometry as geom
import sqlite3, logging
from grass.pygrass.vector import Vector
import log_GRASS as log

def log(folder, fileName):

	file = folder + fileName + '.log'

	logger = logging.getLogger(file)
	hdlr = logging.FileHandler(file)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.WARNING)

# from grass.pygrass.modules import Module

def message (text, filename):
	print "\n\t\t\t\t %s -> %s \n\n" % (text, filename)

def select_Mapset (mapsetName):
	try:
		g.mapset (mapset=mapsetName, flags='c')
		message ('defining mapset', mapsetName)

	except:
		message ('unable to select Mapset', mapsetName)
		pass

def region (format, inFile = "", mapset="PERMANENT", inRaster = "", north=1, south=0, west=0,  east=1, res=1000):

	mapset_at = "@" + mapset

	if format == 'vector':
		g.region( vector = inFile + mapset_at, align = inRaster)
		message ('setting region for vector ', inFile)
	elif format == 'raster':
		# g.region( raster = inFile + mapset_at)
		g.region( raster = inFile)
		message ('setting region for raster ', inFile)
	elif format == 'bounds':
		g.region( n=north, s=south, w=west, e=east, res=res, flags = 'p')
		print 'setting region  n=%d, s=%d, e=%d, w=%d, res=%d' %( north, south, east, west, res)
	elif format == 'bounds_align':
		g.region( n=north, s=south, w=west, e=east, align=inRaster, flags = 'p')
		print 'setting region  n=%.0f, s=%.0f, e=%.0f, w=%.0f, align=%s' %( north, south, east, west, inRaster)
	else:
		message ('unable to set region ', inFile)

	c = grass.region()

	print 'west=%d \t east=%d' % (c['w'], c['e'])
	print 'north=%d \t south=%d' % (c['n'], c['s'])
	print 'ewres=%s \t nsres=%s' % (c['ewres'], c['nsres'])


	# return region parameters
	return c

def select_Files (type, pattern, exclude="", mapset="PERMANENT"):
	# return str(grass.read_command('g.list', type=type, pattern=pattern, exclude=exclude, sep=',', flags='m'))
	return str(grass.read_command('g.list', type=type, pattern=pattern, exclude=exclude, sep=',')).rstrip('\r\n')
	 
def import_Vector (inFile, outFile):
	grass.run_command('v.in.ogr', input=inFile, output=outFile, overwrite=True)
	
def unpack_Vector (inFile, outFile, inDir):

	in_Name = inDir + "/" + inFile

	try:
		grass.run_command('v.unpack', input=in_Name, output=outFile, overwrite=True)
		message ('unpacking file', in_Name)

	except:
		message ('unable to inpack', in_Name)
		pass	

def unpack_Raster (inFile, outFile, inDir):

	in_Name = inDir + "/" + inFile

	try:
		grass.run_command('r.unpack', input=in_Name, output=outFile, overwrite=True, flags='o')
		message ('unpacking file', in_Name)

	except:
		message ('unable to inpack', in_Name)
		pass		
				
def import_CSV (inFile, outFile, x, y, sep, cols, skip):

	try:
		grass.run_command('v.in.ascii', input=inFile, output=outFile, x=x, y=y, separator=sep, columns=cols, skip=skip, overwrite=True)
		message ('importing file', inFile)

	except:
		message ('unable to import', inFile)
		pass

def import_Raster (inFile, outFile):

	try:
		grass.run_command('r.in.gdal', input=inFile, output=outFile, flags='eo', overwrite=True)
		message ('importing file', inFile)

	except:
		message ('unable to import', inFile)
		pass

def import_Raster_Band (inFile, outFile, band):
	grass.run_command('r.in.gdal', input=inFile, output=outFile, band=band, flags='eo', overwrite=True)

def import_NETCDF (inFile, outFile, level):

	in_File = "NETCDF:\"" + inFile + "\""
	
	print ("r.in.gdal input=%s, output=%s") % (in_File, outFile)

	grass.run_command('r.in.gdal', input=in_File, output=outFile, band=str(level), flags='o', overwrite=True)	

def import_Table (inFile, outFile):

	try:
		grass.run_command('db.in.ogr', input=inFile, output=outFile, overwrite=True)
		grass.run_command('db.describe', table=outFile, flags="c")
		grass.run_command('db.select', sql="Select *  from " + outFile, flags="c")

		message ('importing file', inFile)

	except:
		message ('unable to import', inFile)
		pass

def join_Table (inFile, inTable, columnFile, columnTable, subset_columns):

	try:
		grass.run_command('v.db.join', map=inFile, column=columnFile, other_table=inTable, other_column=columnTable, subset_columns=subset_columns, overwrite=True)
		message ('joining table', inTable)		

	except:
		message ('unable to join table', inTable)
		pass
		
def export_File (format, inFile, outFile, outDir=var.DB, type='Int16'):
	
	if format == 'vector':
		message ('v.out.ogr ', outFile)
		grass.run_command('v.out.ogr', input=inFile, output=outDir, output_layer=outFile, format='ESRI_Shapefile', overwrite=True)

	elif format == 'raster':
		message ('r.out.gdal ', outFile)
		out_Name = outDir + "/" + outFile
		grass.run_command('r.out.gdal', input=inFile, output=out_Name, format='GTiff', createopt='TFW=YES,COMPRESS=LZW', overwrite=True)

	elif format == 'stack':
		message ('r.out.gdal ', outFile)	
		out_Name = outDir + "/" + outFile
		grass.run_command('r.out.gdal', input=inFile, output=out_Name, format='GTiff', nodata=-9999, type=type, createopt='PROFILE=GeoTIFF,TFW=YES', overwrite=True, flags="c")

	else:
		message ('unable to export file ', inFile)
	
def export_CSV (inFile, outFile, columns, type='point', separator=';'):
	message ('v.out.ascii  ', outFile)
	grass.run_command('v.out.ascii', input=inFile, output=outFile, type=type, columns=columns, separator=separator, flags='c', overwrite=True)

def reproject_Raster (location, mapset, inFile):

	try:
		grass.run_command('r.proj', location=location, mapset=mapset, input=inFile, overwrite=True)
		message ('reprojecting file', inFile)

	except:
		message ('unable to reproject', inFile)
		pass

def reproject_Vector (location, mapset, inFile):

	try:
		grass.run_command('v.proj', location=location, mapset=mapset, input=inFile, overwrite=True)
		message ('reprojecting file', inFile)

	except:
		message ('unable to reproject', inFile)
		pass

def reclass_Raster (inFile, outFile, inReclass):

	try:
		grass.run_command('r.reclass', input=inFile, output=outFile, rules=inReclass, overwrite=True)
		message ('reclassifying ', outFile)

	except:
		message ('unable to reclassify ', inFile)
		
def dissolve_Vector (inFile, column):

	TMP_file = "TMP_" + inFile

	# copy_File ('vector', inFile, TMP_file)

	grass.run_command('v.dissolve', input=inFile, output=TMP_file, column=column, overwrite=True)		
		
def make_AOI (outFile):
	message ('v.in.region ', outFile)
	grass.run_command('v.in.region', output=outFile, overwrite=True)

def mkGRID (outFile, rows, cols, width, height, left, lower, type):

	grid = str(rows) + ',' + str(cols)
	box = str(width) + ',' + str(height)
	llcorner = str(left) + ',' + str(lower)

	# grid = str('(\'' + str(rows/100) + '\',\'' + str(cols/100) + '\')')
	# box = str('(\'' + str(int(width)*100) + '\',\'' + str(int(height)*100) + '\')')
	# llcorner = str('(\'' + str(int(left)) + '\',\'' + str(int(lower)) + '\')')

	# parameters = ('map=%s, position=%s, coor=%s, grid=%s, box=%s, overwrite=True' % (outFile, 'coor', llcorner, grid, box))


	# v.mkgrid (map='tes', position='coor', coordinates=llcorner, grid=('43','40'),  box=('43','40'), type='area', overwrite=True )


	try:
		grass.run_command('v.mkgrid', map=outFile, position='coor', coor=llcorner, grid=grid, box=box, breaks=0, type=type, overwrite=True)
		message ('creating vector grid', outFile)
	except:
		message ('unable to mkgrid ', outFile)
		pass

def mkGRID_Raster (outFile, region):

	# https://grasswiki.osgeo.org/wiki/Generate_a_grid_with_sequential_numbers

	# parse region parameters
	c = grass.region()

	# set raster formula
	formula = outFile + " = row() *  " + str(c['cols']) + " + col() - " + str(c['cols'])

	# set raster formula
	try:
		grass.mapcalc(formula, overwrite=True)
		message ('mapcalculator ', formula)
	except:
		message ('unable to create raster grid ', outFile)
		pass

# def rasterize_Vector (inFile, outFile, type='point', column=""):
	# message ('r.to.vect ', inFile)
	# grass.run_command('r.to.vect', input=inFile, output=outFile, type=type, column=column, overwrite=True)	
	
def rasterize_Vector (inFile, outFile, type='area', use='cat', column="", label=""):

	if use == "cat":
		grass.run_command('v.to.rast', input=inFile, output=outFile, type=type, use='cat', overwrite=True)

	elif label == "":
		grass.run_command('v.to.rast', input=inFile, output=outFile, type=type, use=use, attribute_column=column, overwrite=True)
		
	else:

		print ('v.to.rast input=%s, output=%s, type=%s, use=%s, attribute_column=%s, label_column=%s, overwrite=True') % (inFile, outFile, type, use, column, label)
		grass.run_command('v.to.rast', input=inFile, output=outFile, type=type, use=use, attribute_column=column, label_column=label, overwrite=True)
		message ('rasterizing vector', outFile)
		
def vectorize_Raster (inFile, outFile, type='area', column=""):

	message ('r.to.vect ', inFile)
	grass.run_command('r.to.vect', input=inFile, output=outFile, type=type, column=column, overwrite=True)	

def raster_Calculator (formula):

	try:
		grass.mapcalc(formula, overwrite=True)
		message ('mapcalculator ', formula)

	except:
		message ('unable to apply ', formula)
		pass

def raster_Series(inFile, outFile, method):
	
	try:
		grass.run_command('r.series', input=inFile, output=outFile, method=method, overwrite=True)
		message ('calculating ', inFile)

	except:
		message ('unable to calculate ')
		pass
		
def patch_Raster (inFiles, outFile):
	message ('r.patch ', inFiles)
	grass.run_command('r.patch', input=inFiles, output=outFile, overwrite=True)
	
def patch_Vector (inFile, outFile, flag):
	message ('v.patch ', inFile)
	grass.run_command('v.patch', input=inFile, output=outFile, flags=flag, overwrite=True)

def group_Raster (inFiles, outFile):

	grass.run_command('i.group', input=inFiles, group=outFile, overwrite=True)

def add_Columns (inFile, columns):
	message ('v.db.addcolumn ', inFile)
	grass.run_command('v.db.addcolumn', map=inFile, columns=columns, overwrite=True)

def add_Coordinates (inFile, columns):
	message ('v.to.db ', inFile)
	grass.run_command('v.to.db', map=inFile, opt='coor', columns=columns, overwrite=True)		
		
def add_Attributes (query):
	message ('db.execute ', query)
	grass.run_command('db.execute', sql=query, overwrite=True)	
	
def add_Table (inFile, columns):
	message ('v.db.addtable ', inFile)
	grass.run_command('v.db.addtable', map=inFile, columns=columns, overwrite=True)	

def resample_Raster_Stats (inFile, outFile, method):
	grass.run_command('r.resamp.stats', input=inFile, output=outFile, method=method, flags="w", overwrite=True)

def resample_Raster (inFile, outFile):
	message ('r.resample ', outFile)
	grass.run_command('r.resample', input=inFile, output=outFile, overwrite=True)

def resample_Raster_RST (inFile, outFile, ew_res, ns_res):
	message ('r.resamp.rst  ', outFile)
	grass.run_command('r.resamp.rst ', input=inFile, output=outFile, ew_res=ew_res, ns_res=ns_res, overwrite=True)
	
def neighbour_Raster (inFile, outFile, method='average', size='21', selection='', flags=''):
	message ('r.neighbors ', inFile)
	
	if selection == '':
		grass.run_command('r.neighbors', input=inFile, output=outFile, method=method, size=size, flags=flags, overwrite=True)	
	else:
		grass.run_command('r.neighbors', input=inFile, output=outFile, method=method, size=size, selection=selection, flags=flags, overwrite=True)	
		
def clip_Raster (inRaster, inMask):

	TMP_Raster = "TMP_" + inRaster

	# set region
	g.region( raster = inMask, flags='pa')
	
	# duplicate raster
	copy_File ('raster', inRaster, TMP_Raster)
	
	# clip raster
	raster_Calculator (
		'%s = if (isnull(%s), null(),  %s)' % 
		(inRaster, inMask, TMP_Raster))	

	# clean files
	remove_File ('raster', TMP_Raster)
	
def clip_Raster_Inverse (inRaster, inMask):

	TMP_Raster = "TMP_" + inRaster

	# set region
	g.region( raster = inMask, flags='pa')
	
	# duplicate raster
	copy_File ('raster', inRaster, TMP_Raster)
	
	# clip raster
	raster_Calculator (
		'%s = if (isnull(%s), %s, null())' % 
		(inRaster, inMask, TMP_Raster))	

	# clean files
	remove_File ('raster', TMP_Raster)
	
def MASK (action, inFile):

	try:
		if action =="remove":
			grass.run_command('r.mask', flags="r", overwrite=True)	
		else:
			grass.run_command('r.mask', raster=inFile, maskcats="*", overwrite=True)
	except:	
		print "Remove or Set MASK Failed"
	
def merge_Raster (raster_1, raster_2, outFile, inMask):

	# set region
	g.region( raster = inMask, flags='pa')
	
	# clip raster
	formula1 = ' if ( isnull('+ raster_1 + '),' + raster_2 + ',' + raster_1 + ')'
	formula2 = outFile + ' =  if ( isnull(' + inMask + '),  null(), ' + formula1 + ')'

	raster_Calculator (formula2)
	
	print formula2
	
def reclass_Raster (inFile, outFile, inReclass):
	grass.run_command('r.reclass', input=inFile, output=outFile, rules=inReclass, overwrite=True)	
	
def stats_Region (inFile, outFile, Zone):
	grass.run_command('r.univar', map=inFile, output=outFile, zones=Zone, separator='comma', flags="t", overwrite=True)	

def clump_Raster (inFile, outFile):
	grass.run_command('r.clump', input=inFile, output=outFile, overwrite=True)	

def stats_Raster (inFile, outFile, flag):
	grass.run_command('r.stats', input=inFile, output=outFile, separator='pipe', flags=flag, overwrite=True)		

def get_Number_Pixels (inFile):

	try:
		n_pixel = int(grass.parse_command('r.univar', map=inFile, flags="g", overwrite=True)['n'].encode('utf-8','ignore').strip())	
	except:
		n_pixel = 0
	
	return n_pixel	
	
def replace_Character (inFile):

	f = open(inFile,'r')
	filedata = f.read()
	f.close()

	newdata = filedata.replace(".000000","").replace("|"," = ")
	
	f = open(inFile,'w')
	f.write(newdata)
	f.close()
	
def remove_File (format, inFile):
	try:
		grass.run_command('g.remove', type=format, name=inFile, flags='f')
	except:
		print "delete failed"

def remove_Pattern (format, pattern):
	message ('g.remove ', pattern)
	grass.run_command('g.remove', type=format, pattern=pattern, flags='f')
	
def rename_File (format, oldFile, newFile):

	inFiles = oldFile + ',' + newFile 
		
	if format == 'vector':
		grass.run_command('g.rename', vector=inFiles, overwrite=True)
		message ('renaming ', oldFile)
	elif format == 'raster':
		grass.run_command('g.rename', raster=inFiles, overwrite=True)
		message ('renaming ', inFiles)
	else:
		message ('unable to rename ', oldFile)
	
def copy_File (format, inFile, outFile):

	copy = inFile + ',' + outFile

	if format == "vector":
		grass.run_command('g.copy', vector=copy, overwrite=True)
	elif format == "raster":
		grass.run_command('g.copy', raster=copy, overwrite=True)
	else:
		print "none"

def do_Colors (inFile, color, flag='e'):
	try:
		return grass.parse_command('r.colors', map=inFile, color=color, flags=flag,overwrite=True)
	except: 
		print "error"
	
def metadata_Raster (inFile):
	message ('r.info ', inFile)
	return grass.parse_command('r.info', map=inFile, flags='g', overwrite=True)		

def resolution_Raster(inFile):
	message ('get resolution m2 ', inFile)
	return float(metadata_Raster (inFile)['nsres'].encode('utf-8','ignore'))

def maxValue_Raster (inFile):

	message ('get max value ', inFile)	
	try:
		return float(grass.parse_command('r.univar', map=inFile, flags='g', overwrite=True)['max'].encode('utf-8','ignore'))
	except:
		return 0
	
def sumValues_Raster (inFile):
	message ('sum raster values ', inFile)
	return float(grass.parse_command('r.univar', map=inFile, flags='g', overwrite=True)['sum'].encode('utf-8','ignore'))
	
def numFeatures_Vector (inFile):
	message ('get number features ', inFile)
	return int(grass.parse_command('v.info', map=inFile, flags='t', overwrite=True)['points'].encode('utf-8','ignore'))
		
def edit_Vector (outFile, tool='create'):
	message ('v.edit ', outFile)
	grass.run_command('v.edit', tool=tool, map=outFile, overwrite=True)
	
def extract_Vector (inFile, outFile, query):
	message ('v.extract ', outFile)
	grass.run_command('v.extract', input=inFile, output=outFile, where=query, overwrite=True)
	
def buffer_Vector (inFile, outFile, column, type='point', layer=1):
	message ('v.buffer ', outFile)
	grass.run_command('v.buffer', input=inFile, output=outFile, column=column, type=type, layer=layer, flags='t', overwrite=True)
	
def buffer_Raster (inFile, outFile, distances):
	message ('r.buffer ', outFile)
	grass.run_command('r.buffer', input=inFile, output=outFile, distances=distances,units='meters', overwrite=True)
	
def select_DB ( sql):
	message ('db.select ', sql)
	return float(grass.read_command('db.select', sql=sql, flags="c", separator='comma', overwrite=True).strip())

def build_Topology (inFile):
	message ('v.build ', inFile)
	grass.run_command('v.build', map=inFile, overwrite=True)
	
def display_Map (inFile, type):

	grass.run_command('d.mon', start="wx1", resolution = '1')

	if type == 'vector':
		grass.run_command('d.vect', map=inFile, overwrite=True)	
	else:
		grass.run_command('d.rast', map=inFile, overwrite=True)	
		
	grass.run_command('d.redraw', verbose="true")

def circle_Raster (inFile, east, north, max):
	message ('r.circle ', inFile)
	grass.run_command('r.circle', output=inFile, coordinates=str(east) + ',' + str(north), max=max, overwrite=True, flags='b')

def query_Attribute (inFile, columns, sql, flag):
	message ('v.db.select ', sql)
	return (grass.read_command('v.db.select', map=inFile, columns=columns, where=sql, overwrite=True, flags=flag).strip())
	
def set_NULLs (inFile, value):
	grass.run_command('r.null',map=inFile, setnull=value, overwrite=True)

def points_in_Polygons (inPoint, outPoint, inPoly, pointColumn, polyColumn):	

	# duplicate raster
	copy_File ('vector', inPoint, outPoint)	
	
	# ADD column
	add_Columns (inFile=outPoint, columns=pointColumn + ' varchar(50)')
		 
	# retrieve data
	grass.run_command('v.what.vect', map=outPoint, column=pointColumn, query_map=inPoly, query_column=polyColumn, overwrite=True)
