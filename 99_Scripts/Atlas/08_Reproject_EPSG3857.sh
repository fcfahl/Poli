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

	export script_PATH='C:/OSGeo4W/apps/grass/grass-7.0.3/scripts/'
	export PG_PATH='C:/Program Files/PostgreSQL/9.5/bin/'
	export OSGEO_PATH='C:/OSGeo4W64/bin/'

	# export PG_PATH=''

	export IFS=" "
	export delimiter=";"

	export DB_Driver="pg"
	export DB_Host="localhost"
	export DB_Name="lulc"
	export DB_Name2="lulc_epsg3857"
	export DB_Format="PostgreSQL"
	export DB_User="postgres"
	export DB_PWD="rosana"
	export DB_Port="5432"
	export DB_Schema="public"

	export DB_Schema1="original"
	export DB_Schema2="dissolved"

	export PGHOST=localhost
	export PGPASSWORD=${DB_PWD}

	export merged_Tables="a000_atlas_2006_merged"

	export DSN="${DB_Driver}:host=${DB_Host} dbname=${DB_Name} user=${DB_User} password=${DB_PWD}"
	export out_Folder="${LOCATION}/02_Output/01_Vector/01_UrbanAtlas_2006/"
	export out_Dump="./2006/ExportDB/Atlas_2006_Tables.dump"
	export out_Dump_Table="${out_Folder}Atlas_2006_Merged.dump"
	export out_Dump_chunks="E:/04_GRASS_database/60_LULC_EPSG_3035/02_Output/01_Vector/01_UrbanAtlas_2006/chunks/Atlas_2006_split.dump.gz."


}

function exe_PSQL () {

	local DB=${1} 
	

	if [ -z "${2}" ]; then
		"${PG_PATH}"psql -h ${DB_Host} -U ${DB_User} -d ${DB}
	else
		"${PG_PATH}"psql -h  ${DB_Host} -U ${DB_User} -d ${DB} -t -c "${2} ;"
	fi

}

function drop_PostGIS_Table () {
	exe_PSQL "DROP TABLE IF EXISTS \"${1}\""
}

function vacuum_PostGIS () {
	local table=${1}

	"${PG_PATH}"vacuumdb -f -v -d ${DB_Name} -U ${DB_User} -t ${table}
}

function create_User () {
	"${PG_PATH}"createuser  "CREATE USER ${DB_User} WITH PASSWORD ${DB_PWD};"
}

function create_Scheme () {

	local schema=${1}

	exe_PSQL ${DB_Name2} "CREATE SCHEMA ${schema}"
}

function create_Database () {
	"${PG_PATH}"createdb -U ${DB_User} ${DB_Name2}
	exe_PSQL ${DB_Name2} "CREATE ROLE ${DB_Role} LOGIN"
	exe_PSQL ${DB_Name2} "CREATE EXTENSION postgis"
	# exe_PSQL ${DB_Name2} "CREATE EXTENSION postgis_topology"

	create_Scheme ${DB_Schema2}
}

function copy_Database () {
	"${PG_PATH}"pg_dump -h ${DB_Host} -U ${DB_User} -d ${DB_Name} -n ${DB_Schema2} --blobs | psql -h ${DB_Host} -U ${DB_User} -d  ${DB_Name2} 
}

function reproject_Database () {
	"${PG_PATH}"pg_dump -h ${DB_Host} -U ${DB_User} -d ${DB_Name} -n ${DB_Schema2} --blobs | psql -h ${DB_Host} -U ${DB_User} -d  ${DB_Name2} 
}

function get_Table_Names {

	# Create new table
		SQL_Query="SELECT table_name
			FROM information_schema.tables
			WHERE table_type = 'BASE TABLE'
			AND table_schema = '${DB_Schema2}'
			AND NOT table_name = 'spatial_ref_sys'
			AND NOT table_name = 'layer_styles'
			ORDER BY table_type, table_name
			"

	 # Execute Query
		export list_Names=$(exe_PSQL ${DB_Name2}  "${SQL_Query}")
		
		echo list_Names
}

function project_Tables {

	# Get table names
		get_Table_Names

	for name in ${list_Names}
	do
	
		out_Name=`echo ${name} | cut -d'_' -f1 `'_epsg3857'
		echo -e "reproject ${DB_Schema2}.${name} ..... ${out_Name}"
		
		SQL_Query="
		
			DROP TABLE if exists ${out_Name};
			CREATE TABLE ${out_Name} AS SELECT * FROM ${DB_Schema2}.${name};
			UPDATE ${out_Name} SET geom = ST_SetSRID(geom, 3857);		
			ALTER TABLE ${out_Name} ADD CONSTRAINT enforce_srid_the_geom CHECK (st_srid(geom) = (3857));
			DROP TABLE if exists ${DB_Schema2}.${name};
		"


		 # Execute Query
			exe_PSQL ${DB_Name2} "${SQL_Query}" 
	done

}


export_Parameters
create_Database
copy_Database
project_Tables
