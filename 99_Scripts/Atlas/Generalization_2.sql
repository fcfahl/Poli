		DROP TABLE IF EXISTS ${out_Table};	

		--Creates the target table
			CREATE TABLE ${out_Table} AS (
			SELECT cities, item, code, (st_dump(wkb_geometry)).* 
			FROM ${in_Table} );
			
			
			CREATE TABLE rings AS (
			SELECT st_exteriorRing((st_dumpRings(geom)).geom) AS g 
			from ${out_Table}
			);
			
			CREATE TABLE simplerings AS (
			SELECT st_simplifyPreserveTopology(st_linemerge(st_union(g)), 10000) AS g 
			FROM rings
			);
			
			CREATE TABLE simplelines AS (
			SELECT (st_dump(g)).geom AS g 
			FROM simplerings
			);
			
			CREATE TABLE simplepolys AS ( 
			SELECT (st_dump(st_polygonize(distinct g))).geom AS g
			FROM simplelines
			);
			
			ALTER TABLE simplepolys  ADD COLUMN gid serial primary key;
			CREATE INDEX simplepolys_geom_gist on simplepolys using gist(g);
			
			CREATE TABLE simpletable AS (
			SELECT cities, item, code, g
			FROM ${in_Table} d, simplepolys s
			WHERE st_contains(d.geom, st_pointOnSurface(s.g))
			);
			
			CREATE TABLE simple_departement AS (
			SELECT code_dept, st_collect(geom) AS geom
			FROM simpledep
			GROUP by code_dept
			);