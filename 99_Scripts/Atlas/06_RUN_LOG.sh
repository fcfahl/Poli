#!/bin/bash -x
# ========================================================================================================
# FILE: 
# 
# DESCRIPTION:
# Process: 	...
# 
# Notes:	
# 
# Rev 1.1    Mar 2015  Fernando Fahl
# ==========================================================================================================
#______________________Check GRASS
if [ -z "$GISBASE" ] ; then
    echo "You must be in GRASS GIS to run this program." 1>&2
    exit 1
fi

name="Atlas.out"

# ( sh 03_RUN.sh ) | tee BIOGAS.log

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>${name} 2>&1

sh Atlas_PostGIS_Dissolve.sh