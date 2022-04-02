import json
import base64
import gzip
import zlib

from support import import_from_sprite_sheet

class Map:
    def __init__(self,path) -> None:
        # load json file
        self.json_obj = json.loads(path)
        # extract general info
        self.mapsize = (self.json_obj['width'],self.json_obj['height'])
        # tilesize (single value if square or tuple)
        self.tilesize = self.json_obj['tileheight'] if self.json_obj['tileheight'] == self.json_obj['tilewidth'] else (self.json_obj['tilewidth'],self.json_obj['tileheight'])
        # layers (list)
        self.layers = self.json_obj['layers']
        # tilesets (list)
        self.tilesets = []
        # map dictionary
        self.mapdata = {}

    # process layer data and create map dictionary
    def process_layers(self):
        for layer in self.layers:
            compression = layer.get('compression')
            encoding = layer.get('encoding')
            name = layer['name']

            if encoding:
                self.mapdata[name] = self.decode_layer_data(layer['data'],encoding,compression)
            else:
                # data is a list of GIDs
                layer_data = []
                row = []
                for idx in range(0,len(layer['data'])):
                    row.append(layer['data'][idx])
                    if idx % self.mapsize[0] == self.mapsize[0] - 1:
                        layer_data.append(row)
                        row = []
                self.mapdata[name]  = layer_data

    # transform layer data into lists of GIDs
    def decode_layer_data(self,data,encoding,compression):
        byte_data = self.unpack_layer_data(data,encoding,compression)
        layer_data = []
        row = []
        max_idx = self.mapsize[0] * 4
        for idx in range(0,len(byte_data),4): # ommit additional bytes for now
            row.append(byte_data[idx])
            if idx % max_idx == max_idx - 1:
                layer_data.append(row)
                row = []

        return layer_data

    # unpack encoded and compressed data
    def unpack_layer_data(self,data,encoding,compression):
        dec_data = None
        if encoding == 'base64':
            dec_data = base64.decompress(data)
            if compression == 'gzip':
                return gzip.decompress(dec_data)
            if compression == 'zlib':
                return zlib.decompress(dec_data)

        return dec_data

    def process_tilesets(self):
        for tileset in self.json_obj['tilesets']:
            path = tileset['image']
            tilesize = (tileset['tilewidth'],tileset['tileheight'])
            Tileset(tileset['firstgid'],import_from_sprite_sheet(path,tilesize))

class Tileset:
    def __init__(self,gid,tiles) -> None:
        self.first_gid = gid
        self.tiles = tiles