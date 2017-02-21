from LULC_variables import *
from grass_functions import *  


def import_LULC (obj): 
    
    inFile = obj.outFileFull + "_EPSG3857.tif"
    
    #_________import Raster
#    import_Raster(inFile=inFile, outFile=obj.outFile)  

    # __________ set colortable
    do_Colors_Rules (inFile=obj.outFile, rules=obj.color)

    # __________ set categories
    do_Cats_Rules (inFile=obj.outFile, rules=obj.cats)
    
    
    
def import_MODIS (obj, type): 
    
    inFile = obj.outFileFull + "_Type" + str(type) + "_EPSG3857.tif"
    outFile = obj.outFile + "_Type" + str(type)
    
    #_________import Raster
    import_Raster(inFile=inFile, outFile=outFile)  

    # __________ set colortable
    do_Colors_Rules (inFile=outFile, rules=obj.color)

    # __________ set categories
    do_Cats_Rules (inFile=outFile, rules=obj.cats)
    
    

if __name__ == "__main__": 
    
    #_________change mapset
    select_Mapset(mapset="PERMANENT")
    
#    LULC = [GLC_2000['2000'], GlobCover['2005'],GlobCover['2009']]
#    LULC = [ESA['2000'],ESA['2005'],ESA['2010'],Corine['1990'],Corine['2000'],Corine['2006'],Corine['2012']]
#    LULC = [GHSL['1975'],GHSL['1990'],GHSL['2000'],GHSL['2015'],GLand30['2010']]


#    LULC = [GHSL['1975'],GHSL['1990'],GHSL['2000'],GHSL['2015']]
#
#    for obj in LULC:
#                  
#        import_LULC (obj)
                  
#                  
#    
    for year in range(2001, 2013):
        
        for type in [1,2,3,4,5]:            
            
        
            obj = MODIS[str(year)]
            import_MODIS (obj, type)

