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
	local topo_1="${in_Name}_1"
	local topo_2="${in_Name}_2"
	local index1="${in_Name}_gist"

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
		"

		SQL_Query2="
			DROP TABLE IF EXISTS rings;
			CREATE TABLE rings AS (
			SELECT st_exteriorRing((st_dumpRings(geom)).geom) AS g
			from ${out_Table}
			);
		"

		SQL_Query3="
			DROP TABLE IF EXISTS simplerings;
			CREATE TABLE simplerings AS (
			SELECT st_simplifyPreserveTopology(st_linemerge(st_union(g)), 0.001) AS g
			FROM rings
			);
		"

		SQL_Query4="
			DROP TABLE IF EXISTS simplelines;
			CREATE TABLE simplelines AS (
			SELECT (st_dump(g)).geom AS g
			FROM simplerings
			);
		"

		SQL_Query5="
			DROP TABLE IF EXISTS simplepolys;		
			CREATE TABLE simplepolys AS (
			SELECT (st_dump(st_polygonize(distinct g))).geom AS g
			FROM simplelines
			);
		"

		SQL_Query6="
			ALTER TABLE simplepolys  ADD COLUMN gid serial primary key;
			CREATE INDEX simplepolys_geom_gist on simplepolys using gist(g);
			);
		"

		SQL_Query7="
			DROP TABLE IF EXISTS simpletable;				
			CREATE TABLE simpletable AS (
			SELECT cities, item, code, g
			FROM ${in_Table} d, simplepolys s
			WHERE st_contains(d.geom, st_pointOnSurface(s.g))
			);
		"

		SQL_Query8="
			DROP TABLE IF EXISTS simpledep;			
			CREATE TABLE simpledep AS (
			select d.code, s.g as geom
			FROM ${in_Table} d, simplepolys s
			WHERE st_intersects(d.geom, s.g)
			AND st_area(st_intersection(s.g, d.geom))/st_area(s.g) > 0.5
			);
		"

		SQL_Query9="
			DROP TABLE IF EXISTS finaltable;				
			CREATE TABLE finaltable AS (
			SELECT cities, item, code, st_collect(geom) AS geom
			FROM simpledep
			GROUP by code
			);
		"

	 # Execute Query
	 echo -e "\nTABLE: \t\t\t ${in_Table}"
		echo -e "\nQUERY 1 - Creates the target table -> \t\t\t\t\tStarting time: " $(date +"%T")
		exe_PSQL "${SQL_Query1}"

		vacuum_PostGIS ${out_Table}

		echo -e "\nQUERY 2 - .... -> \t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query2}"

		echo -e "\nQUERY 3 - .... -> \t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query3}"

		echo -e "\nQUERY 4 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query4}"

		echo -e "\nQUERY 5 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query5}"

		echo -e "\nQUERY 6 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query6}"

		echo -e "\nQUERY 7 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query7}"

		echo -e "\nQUERY 8 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query8}"

		echo -e "\nQUERY 9 - .... -> \t\t\t\t\tStarting time:  $(date +"%T") \n\n"
		exe_PSQL "${SQL_Query9}"

		vacuum_PostGIS ${out_Table}

		echo -e "\n___________________________________________"



		echo -e "\n\n\t\t\t\t\t\tEnding time:  $(date +"%T") \n\n"

}



export_Parameters
fix_topology "de040l_saarbrucken"  "original" "de040l_saarbrucken_diss" "dissolved"
