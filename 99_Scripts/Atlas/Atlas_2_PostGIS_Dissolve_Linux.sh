#!/bin/bash
# ========================================================================================================
# FILE: 
# 
# DESCRIPTION:
# Process: 	...
# 
# Notes:	....
# 
# Rev 1.1    Mar 2015  Fernando Fahl
# ==========================================================================================================

function export_Parameters () {

	eval `g.gisenv`
	LOCATION=$GISDBASE/$LOCATION_NAME

	export script_PATH='C:/OSGeo4W/apps/grass/grass-7.0.3/scripts/'
	export PG_PATH='C:/Program Files/PostgreSQL/9.4\bin/'
	
	export PG_PATH=''
	
	export IFS=" "
	export delimiter=";"

	export DB_Driver="pg"
	export DB_Host="localhost"
	export DB_Name="lulc"
	export DB_Format="PostgreSQL"
	export DB_User="postgres"
	export DB_PWD="postgres"
	export DB_Port="5432"
	export DB_Schema="public"
	
	export PGHOST=localhost
	export PGPASSWORD=${DB_PWD}
	
	export merged_Tables="a000_atlas_2006_merged"	
	
	export DSN="${DB_Driver}:host=${DB_Host} dbname=${DB_Name} user=${DB_User} password=${DB_PWD}"	
	export out_Folder="${LOCATION}/02_Output/01_Vector/01_UrbanAtlas_2006/"	
	export out_Dump="${out_Folder}Atlas_2006_Tables_Diss.dump"	
	export out_Dump_Table="${out_Folder}Atlas_2006_Merged.dump"	


}

function exe_PSQL () {

	if [ -z "${1}" ]; then	
		"${PG_PATH}"psql -h ${DB_Host} -U ${DB_User} -d ${DB_Name} 
	else	
		"${PG_PATH}"psql -h  ${DB_Host} -U ${DB_User} -d ${DB_Name} -t -c "${1} ;"
	fi
	
}

function drop_PostGIS_Table () {
	exe_PSQL "DROP TABLE IF EXISTS \"${1}\""
}

function vacuum_PostGIS () {
	"${PG_PATH}"vacuumdb -a
}

function create_User () {
	"${PG_PATH}"createuser  "CREATE USER ${DB_User} WITH PASSWORD ${DB_PWD};"
}

function create_Database () {	
	"${PG_PATH}"createdb -U ${DB_User} ${DB_Name} 		
	exe_PSQL "CREATE ROLE ${DB_Role} LOGIN"		
	exe_PSQL "CREATE EXTENSION postgis"		
	exe_PSQL "CREATE EXTENSION postgis_topology"	
}

function create_Scheme () {	
	exe_PSQL "CREATE SCHEMA yourschema"
}

function dissolve_PostGIS () {	

	local in_File=${1}
	local out_File="${1}_gl"

	now=$(date +"%T")
	echo -e "\n_______________Starting time : $now"
	
	SQL_Query=" DROP TABLE IF EXISTS ${out_File};
	 create table ${out_File} AS
	 SELECT cities,item,code,ST_Union(ST_MakeValid(ST_SnapToGrid(geom,0.0001)))
	 FROM ${in_File}
	 GROUP BY code,cities,item;
	 DROP TABLE IF EXISTS ${in_File};
	 "
	 
	 # Execute Query	
		exe_PSQL "${SQL_Query}"
		
	now=$(date +"%T")
	echo -e "\n_______________Ending time : $now\n\n\n"
	
}

function generalize {

	local in_Table="${1}"
	local out_Table="${1}_gl"	


	echo -e "\nSimplifying table ..... ${out_Table}"
	
	local now=$(date +"%T")
	echo -e "\n_______________Starting time : $now"
	
	#~ see tutorial on https://trac.osgeo.org/postgis/wiki/UsersWikiSimplifyWithTopologyExt
	
	# Create new table
		SQL_Query="
		
	
		DROP TABLE IF EXISTS ${out_Table};	

		--Creates the target table
			CREATE TABLE ${out_Table} AS (
			SELECT cities, item, code, ST_SimplifyPreserveTopology(wkb_geometry, 0.0005) AS geom
			FROM ${in_Table} );			
		
		--Creates INDEX
			CREATE INDEX geom_gist on ${out_Table} using gist(geom);
		"	
		
		


	 # Execute Query	
		exe_PSQL "${SQL_Query}"


	local now=$(date +"%T")
	echo -e "\n_______________Ending time : $now\n\n\n"
}

function import_UrbanAtlas_2006 () {
	
		cd ./2006/test2/
		
		for files in *.zip
		do						
				file_Name=`echo ${files} | cut -d'.' -f1`
		
				# Decompress 
					echo -e "\nunziping ..... ${files}"						
					unzip -j -o "${in_Folder}${files}" 
					
					
					chmod -R 777 *
					
				# Import to PostGIS
					echo -e "\nimporting ..... ${file_Name}.shp"
					ogr2ogr -f PostgreSQL "PG:host=${DB_Host} user=${DB_User} dbname=${DB_Name} password=${DB_PWD}" ${file_Name}.shp -lco LAUNDER="YES" -nlt PROMOTE_TO_MULTI -overwrite -skipfailures	

				# Generalize Polygons
					generalize ${file_Name}	

				# Dissolve Polygons
					dissolve_PostGIS ${file_Name}				
		
					
				# Remove temp files (leave only zip files)
					rm -f *.shp *.shx *.dbf *.prj *.pdf *.doc *.xml

				
		done	
		
		cd ../..
		
}



function get_Table_Names {

	# Create new table
		SQL_Query="SELECT table_name 
			FROM information_schema.tables 
			WHERE table_type = 'BASE TABLE'  
			AND table_schema = 'public'  
			AND NOT table_name = 'spatial_ref_sys' 
			AND NOT table_name = 'layer_styles'  
			AND NOT table_name = '${merged_Tables}' 
			ORDER BY table_type, table_name 
			"
		 
	 # Execute Query	
		export list_Names=$(exe_PSQL "${SQL_Query}") 
}

function create_merged_Table {

	echo -e "\nCreating table ..... ${merged_Tables}"
	
	# Create new table
		SQL_Query="DROP TABLE IF EXISTS ${merged_Tables};
		CREATE TABLE IF NOT EXISTS ${merged_Tables} (cities varchar(255), item varchar(100), code varchar(10) );
		SELECT AddGeometryColumn('${merged_Tables}','geom',3035,'MULTIPOLYGON',2);"
		 
	 # Execute Query	
		exe_PSQL "${SQL_Query}"
}


function merge_Tables {

	# Get table names
		get_Table_Names

	# Create merged Table
		create_merged_Table		
	
	for name in ${list_Names}
	do
		echo -e "inserting ..... ${name}"
		
		SQL_Query=" ALTER TABLE ${name} ALTER COLUMN st_union 
					SET DATA TYPE geometry(MULTIPOLYGON) USING ST_Multi(st_union);

					ALTER TABLE ${name} ALTER COLUMN st_union TYPE geometry(MULTIPOLYGON, 3035) USING ST_SetSRID(st_union, 3035);					
					
					INSERT INTO ${merged_Tables} (cities, item, code, geom)
					SELECT
						cities, item, code, st_union
					FROM
						${name}"
						
		 # Execute Query	
			exe_PSQL "${SQL_Query}"			
	done

}

function export_UrbanAtlas_2006 {	

		# "${PG_PATH}"pg_dump -Fc ${DB_Name} > ${out_Dump}
		"${PG_PATH}"pg_dump -a -h  ${DB_Host} -U ${DB_User} -d ${DB_Name} -t ${merged_Tables} > ${out_Dump_Table}  		
}


export_Parameters
# create_Database
import_UrbanAtlas_2006
#~ merge_Tables
#~ export_UrbanAtlas_2006