test -r ~/.alias && . ~/.alias
PS1='GRASS 7.0.4 (EPSG3857):\w > '
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
export GRASS_VERSION=7.0.4
export GRASS_GNUPLOT="gnuplot -persist"
export GRASS_PYTHON=python
export GRASS_PROJSHARE=/usr/share/proj
export GRASS_PAGER=more
export GRASS_HTML_BROWSER=xdg-open
export GRASS_ADDON_BASE=/home/fcfahl/.grass7/addons
export PATH="/usr/lib64/grass70/bin:/usr/lib64/grass70/scripts:/home/fcfahl/.grass7/addons/bin:/home/fcfahl/.grass7/addons/scripts:/usr/lib64/qt-3.3/bin:/usr/lib64/ccache:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/home/fcfahl/.local/bin:/home/fcfahl/bin"
export HOME="/home/fcfahl"
