		DROP TABLE IF EXISTS ${out_Table};	

		--Creates the target table
			CREATE TABLE ${out_Table} AS (
			SELECT cities, item, code, (st_dump(wkb_geometry)).* 
			FROM ${in_Table} );
		
		--Creates INDEX
			CREATE INDEX "${out_Table}_gist" on ${out_Table} using gist(geom);

		-- adds the new geom column that will contain simplified geoms
			ALTER TABLE ${out_Table} ADD COLUMN simple_geom geometry(POLYGON, 3035);
		
		-- create new empty topology structure
			SELECT CreateTopology('topo1',3035,0);
		
		-- add all polygons to topology in one operation as a collection
			SELECT ST_CreateTopoGeo('topo1',ST_Collect(wkb_geometry))
			FROM ${in_Table};
			
		-- Create a new topology based on the simplification of existing one	
			SELECT CreateTopology('topo2',3035,0);

			SELECT ST_CreateTopoGeo('topo2', geom)
			FROM (
				select ST_Collect(st_simplifyPreserveTopology(geom, 10000)) as geom
				from topo1.edge_data
			) as foo;
			
		-- Retrieves polygons by comparing surfaces 		
			WITH simple_face AS (
				SELECT st_getFaceGeometry('topo2', face_id) AS geom
				FROM topo2.face
				WHERE face_id > 0
			) 
			UPDATE ${out_Table} d set simple_geom = sf.geom
			FROM simple_face sf
			WHERE st_intersects(d.geom, sf.geom)
			AND st_area(st_intersection(sf.geom, d.geom))/st_area(sf.geom) > 0.5;
		"	