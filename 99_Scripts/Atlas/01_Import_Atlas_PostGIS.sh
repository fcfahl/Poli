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
	local table=${1}

	"${PG_PATH}"vacuumdb -f -v -d ${DB_Name} -U ${DB_User} -t ${table}
}

function create_User () {
	"${PG_PATH}"createuser  "CREATE USER ${DB_User} WITH PASSWORD ${DB_PWD};"
}

function create_Scheme () {

	local schema=${1}

	exe_PSQL "CREATE SCHEMA ${schema}"
}

function create_Database () {
	"${PG_PATH}"createdb -U ${DB_User} ${DB_Name}
	exe_PSQL "CREATE ROLE ${DB_Role} LOGIN"
	exe_PSQL "CREATE EXTENSION postgis"
	exe_PSQL "CREATE EXTENSION postgis_topology"

	create_Scheme ${DB_Schema1}
	create_Scheme ${DB_Schema2}
}

function generalize {

	local in_Name=${1}
	local in_Table="${DB_Schema1}.${in_Name}"
	local out_Table="${DB_Schema1}.${in_Name}_gl"
	local diss_Table="${DB_Schema2}.${in_Name}_diss"
	local index1="${in_Name}_gl_gist"
	local index2="${in_Name}_diss_gist"

	#~ see tutorial on https://trac.osgeo.org/postgis/wiki/UsersWikiSimplifyWithTopologyExt

	# Create new table
		SQL_Query1="
			DROP TABLE IF EXISTS ${out_Table};

			--Creates the target table
				CREATE TABLE ${out_Table} AS (
				SELECT cities, item, code, wkb_geometry AS geom
				FROM ${in_Table} );
				DROP TABLE IF EXISTS ${in_Table};

				ALTER TABLE ${out_Table} RENAME TO ${in_Name};
		"

		SQL_Query2="
			DROP TABLE IF EXISTS ${diss_Table};
			create table ${diss_Table} AS
			SELECT cities,item,code, ST_Union(ST_MakeValid(ST_SnapToGrid(geom,0.0001))) AS geom
			FROM ${in_Table}
			GROUP BY code,cities,item;
		"

		SQL_Query3="
		--Creates INDEX
			CREATE INDEX ${index1} on "${in_Table}" using gist(geom);
			CREATE INDEX ${index2} on "${diss_Table}" using gist(geom);
		"

	 # Execute Query
	 echo -e "\nTABLE: \t\t\t ${in_Table}"
	 	echo -e "\nQUERY 1 - Clean data -> \t\t\tStarting time: " $(date +"%T")
		exe_PSQL "${SQL_Query1}"

		echo -e "\nQUERY 2 - Dissolve polygons -> \t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query2}"

		echo -e "\nQUERY 3 - Create Index -> \t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query3}"

		echo -e "\n___________________________________________"

		vacuum_PostGIS ${in_Table}
		vacuum_PostGIS ${diss_Table}

		echo -e "\n\n\t\t\t\t\t\tEnding time:  $(date +"%T") \n\n"

}


function import_UrbanAtlas_2006 () {

		cd ./2006/test/

		for files in *.zip
		do
				file_Name=`echo ${files} | cut -d'.' -f1`

				# Decompress
					echo -e "\nunziping ..... ${files}"
					unzip -j -o "${in_Folder}${files}"

				# Import to PostGIS
					echo -e "\nimporting ..... ${file_Name}.shp"
					"${OSGEO_PATH}"ogr2ogr -f PostgreSQL "PG:host=${DB_Host} user=${DB_User} dbname=${DB_Name} SCHEMAS=${DB_Schema1} password=${DB_PWD}" ${file_Name}.shp -lco LAUNDER="YES" -nlt PROMOTE_TO_MULTI -overwrite -skipfailures

				# Generalize Polygons
					generalize ${file_Name}

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

		# "${PG_PATH}"pg_dump -a -h  ${DB_Host} -U ${DB_User} -d ${DB_Name} > ${out_Dump}
		# "${PG_PATH}"pg_dump -a -h  ${DB_Host} -U ${DB_User} -d ${DB_Name} -t ${merged_Tables} > ${out_Dump_Table}
		
		# export compressed chunks		
		echo "pg_dump --host=${DB_Host} --username=${DB_User} --database=${DB_Name} --schema=${DB_Schema2} --format=t  --blobs --verbose | gzip | split -b 1024m - ${out_Dump_chunks}"
		"${PG_PATH}"pg_dump --host=${DB_Host} --username=${DB_User} --dbname="lulc" --schema="dissolved" --format=t  --verbose | gzip | split -b 1024m - ${out_Dump_chunks}
		

}


export_Parameters
# create_Database
# import_UrbanAtlas_2006
#~ merge_Tables
export_UrbanAtlas_2006
