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
	export DB_Schema3="generalize"
	export DB_Schema4="topo"

	export PGHOST=localhost
	export PGPASSWORD=${DB_PWD}

	export merged_Tables="a000_atlas_2006_merged"

	export DSN="${DB_Driver}:host=${DB_Host} dbname=${DB_Name} user=${DB_User} password=${DB_PWD}"
	export out_Folder="${LOCATION}/02_Output/01_Vector/01_UrbanAtlas_2006/"
	export out_Dump="./2006/ExportDB/Atlas_2006_Tables.dump"
	export out_Dump_Table="${out_Folder}Atlas_2006_Merged.dump"


}

function exe_PSQL () {

	if [ -z "${1}" ]; then
		"${PG_PATH}"psql -h ${DB_Host} -U ${DB_User} -d ${DB_Name}
	else
		"${PG_PATH}"psql -h  ${DB_Host} -U ${DB_User} -d ${DB_Name} -t -c "${1} ;"
	fi
}

function vacuum_PostGIS () {
	local table=${1}

	"${PG_PATH}"vacuumdb -f -v -d ${DB_Name} -U ${DB_User} -t ${table}
}



function fix_topology {

	local in_Name=${1}
	local in_Schema=${2}
	local out_Name=${3}
	local out_Schema=${4}
	local in_Table="${in_Schema}.${in_Name}"
	local out_Table="${out_Schema}.${out_Name}"
	local topo_1="${in_Name}_3"
	local topo_2="${in_Name}_4"
	local index1="${in_Name}_gist2"

	#~ see tutorial on https://trac.osgeo.org/postgis/wiki/UsersWikiSimplifyWithTopologyExt

	# Create new table
		SQL_Query1="

			--Creates the target table
				DROP TABLE IF EXISTS ${out_Table};
				CREATE TABLE ${out_Table} AS (
				SELECT cities, item, code, (st_dump(geom)).*
				FROM ${in_Table} );

			--Creates INDEX
				CREATE INDEX ${index1} on "${out_Table}" using gist(geom);

			-- adds the new geom column that will contain simplified geoms
				ALTER TABLE ${out_Table} ADD COLUMN simple_geom geometry(POLYGON, 3035);
		"

		SQL_Query2="
			-- remove previous topology id
			-- DELETE FROM 	topology.topology
			-- WHERE name = '${topo_1}' or name = '${topo_2}';

			-- DROP SCHEMA '${topo_1}' CASCADE;
			-- DROP SCHEMA '${topo_2}' CASCADE;

			-- create new empty topology structure
				SELECT CreateTopology('${topo_1}',3035,0);
		"

		SQL_Query3="
			-- add all polygons to topology in one operation as a collection
				SELECT ST_CreateTopoGeo('${topo_1}',ST_Collect(geom))
				FROM ${out_Table};
		"

		SQL_Query4="
		-- Create a new topology based on the simplification of existing one
			SELECT CreateTopology('${topo_2}',3035,0);

			SELECT ST_CreateTopoGeo('${topo_2}', geom)
			FROM (
				select ST_Collect(st_simplifyPreserveTopology(geom, 1)) as geom
				from ${topo_1}.edge_data
			) as foo;
		"

		SQL_Query5="
		-- Retrieves polygons by comparing surfaces
		WITH simple_face AS (
			SELECT st_getFaceGeometry('${topo_2}', face_id) AS geom
			FROM ${topo_2}.face
			WHERE face_id > 0
		)
		UPDATE ${out_Table} d set simple_geom = sf.geom
		FROM simple_face sf
		WHERE st_intersects(d.geom, sf.geom)
		AND st_area(st_intersection(sf.geom, d.geom))/st_area(sf.geom) > 0.5;

		-- clean table
		ALTER TABLE ${out_Table} DROP COLUMN geom;
		ALTER TABLE ${out_Table} DROP COLUMN path;

		ALTER TABLE ${out_Table} RENAME COLUMN simple_geom TO geom;

		SELECT topology.DropTopology('${topo_1}');
		SELECT topology.DropTopology('${topo_2}');
		"

	 # Execute Query
	 echo -e "\nTABLE: \t\t\t ${in_Table}"
		echo -e "\nQUERY 1 - Creates the target table -> \t\t\t\t\tStarting time: " $(date +"%T")
		exe_PSQL "${SQL_Query1}"

		echo -e "\nQUERY 2 - create 1st empty topology structure -> \t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query2}"

		echo -e "\nQUERY 3 - create 1st empty topology structure -> \t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query3}"

		echo -e "\nQUERY 4 - create 2nd topology structure -> \t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query4}"

		echo -e "\nQUERY 5 - Retrieves polygons -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query5}"
		vacuum_PostGIS ${out_Table}

		echo -e "\n___________________________________________"


		echo -e "\n\n\t\t\t\t\t\tEnding time:  $(date +"%T") \n\n"

}



export_Parameters
fix_topology "de040l_saarbrucken"  "original" "de040l_saarbrucken_diss2" "dissolved"
