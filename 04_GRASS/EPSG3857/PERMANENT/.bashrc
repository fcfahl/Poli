test -r ~/.alias && . ~/.alias
PS1='GRASS 7.2.0 (EPSG3857):\w > '
grass_prompt() {
	LOCATION="`g.gisenv get=GISDBASE,LOCATION_NAME,MAPSET separator='/'`"
	if test -d "$LOCATION/grid3/G3D_MASK" && test -f "$LOCATION/cell/MASK" ; then
		echo [2D and 3D raster MASKs present]
	elif test -f "$LOCATION/cell/MASK" ; then
		echo [Raster MASK present]
	elif test -d "$LOCATION/grid3/G3D_MASK" ; then
		echo [3D raster MASK present]
	fi
}
PROMPT_COMMAND=grass_prompt
export PATH="/usr/lib/grass72/bin:/usr/lib/grass72/scripts:/home/fcfahl/.grass7/addons/bin:/home/fcfahl/.grass7/addons/scripts:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/rasdaman/bin:/usr/lib/postgresql/9.5/bin:/opt/MRT_Linux/bin/"
export HOME="/home/fcfahl"
