import json
import base64
import gzip
import zlib
import sys

from support import import_from_sprite_sheet

BYTES_PER_GID = 4

class Map:
    def __init__(self,path) -> None:
        # load json file
        with open(path) as json_file:
            self.json_obj = json.load(json_file)
        # extract general info
        self.mapsize = (self.json_obj['width'],self.json_obj['height'])
        # tilesize
        self.tilesize = (self.json_obj['tilewidth'],self.json_obj['tileheight'])
        # tilesets (list)
        self.tilesets = []
        self.firstgids = []
        # map dictionary
        self.mapdata = {}

        self.process_tilesets()
        self.process_layers()
        # delete object , may not be necessary
        self.json_obj = None

    # process layer data and create map dictionary
    def process_layers(self):
        for layer in self.json_obj['layers']:
            compression = layer.get('compression')
            encoding = layer.get('encoding')
            name = layer['name']

            if encoding:
                self.mapdata[name] = self.decode_layer_data(layer['data'],encoding,compression)
            else:
                # data is a list of GIDs or object layer
                # TODO: cleanup and do object layer
                if layer.get('data'):
                    layer_data = []
                    row = []
                    for idx in range(0,len(layer['data'])):
                        row.append(layer['data'][idx])
                        if idx % self.mapsize[0] == self.mapsize[0] - 1:
                            layer_data.append(row)
                            row = []
                    self.mapdata[name] = layer_data

    # transform layer data into lists of GIDs
    # TODO: this is probably not correct if the ID is larger than 8 bit
    #       or if additional flipping or rotation bits are set.
    def decode_layer_data(self,data,encoding,compression):
        byte_data = self.unpack_layer_data(data,encoding,compression)
        layer_data = []
        row = []
        max_idx = self.mapsize[0] * BYTES_PER_GID
        for idx in range(0,len(byte_data),BYTES_PER_GID):
            row.append(byte_data[idx])
            if idx % max_idx == max_idx - BYTES_PER_GID:
                layer_data.append(row)
                row = []

        return layer_data

    # unpack encoded and compressed data
    def unpack_layer_data(self,data,encoding,compression):
        dec_data = None
        if encoding == 'base64':
            dec_data = base64.b64decode(data)
            if compression == 'gzip':
                return gzip.decompress(dec_data)
            if compression == 'zlib':
                return zlib.decompress(dec_data)

        return dec_data

    # convert tileset data into list of sprites
    def process_tilesets(self):
        for tileset in self.json_obj['tilesets']:
            path = '../assets/' + tileset['image']
            tilesize = (tileset['tilewidth'],tileset['tileheight'])
            self.firstgids.append((tileset['firstgid'],tileset['tilecount']))
            self.tilesets.append(Tileset(tileset['name'],tileset['firstgid'],tileset['tilecount'],import_from_sprite_sheet(path,tilesize)))

class Tileset:
    def __init__(self,name,gid,tilecount,tiles) -> None:
        self.name = name
        self.first_gid = gid
        self.tilecount = tilecount
        self.tiles = tiles