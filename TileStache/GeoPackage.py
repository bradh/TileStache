""" Support for GeoPackage tiles, draft Work-in-Progress

GeoPackage is a new thing. Docs are good!

Example configuration:

  {
    "cache": { ... }.
    "layers":
    {
      "roads":
      {
        "provider":
        {
          "name": "geopackage",
	  "geopackage" : "filename.geopackage",
          "tileset": "blue_tiles"
        }
      }
    }
  }

GeoPackage provider parameters:

  geopackage:
    Required local file path to a GeoPackage file.

  tileset:
    The tiles data table name
"""

from urlparse import urlparse, urljoin
from os.path import exists
import StringIO
import sys
from PIL import Image

try:
    from sqlite3 import connect as _connect
except ImportError:
    # Heroku appears to be missing standard python's
    # sqlite3 package, so throw an ImportError later
    def _connect(filename):
        raise ImportError('No module named sqlite3')

from ModestMaps.Core import Coordinate

class Provider:
    """ GeoPackage provider.
    
        See module documentation for explanation of constructor arguments.
    """
    def __init__(self, layer, geopackage, tileset):
        """
        """
        sethref = urljoin(layer.config.dirpath, geopackage)
        scheme, h, path, q, p, f = urlparse(sethref)
        
        if scheme not in ('file', ''):
            raise Exception('Bad scheme in GeoPackage provider, must be local file: "%s"' % scheme)
        
        self.layer = layer
        self.geopackage = geopackage
        self.tileset = tileset
        self.db = _connect(path)
        self.db.text_factory = bytes
        self.tilequery = 'SELECT tile_data FROM {tileset} WHERE zoom_level=? AND tile_column=? AND tile_row=?'.format(tileset=tileset)
        (self.mime_type,) = self.db.execute("SELECT mime_type FROM raster_format_metadata WHERE r_table_name=?", (tileset,)).fetchone()
    
    def renderTile(self, width, height, srs, coord):
        """ Retrieve a single tile, return a TileResponse instance.
        """
	content = self.db.execute(self.tilequery, (coord.zoom, coord.column, coord.row)).fetchone()
	content = content and content[0] or None
	formats = {'image/png': 'PNG', 'image/jpeg': 'JPEG', None: None}
	blobIO = StringIO.StringIO(content)
	return Image.open(blobIO)
