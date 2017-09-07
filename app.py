# -*- coding: utf-8 -*-
#######################################################3
# xuxiang@sensetime.com
# 2017.9.7
# 
# for more usage details, refer to http://blog.csdn.net/u011393661/article/details/14053113 
###

import os
import random
from urllib2 import urlopen, URLError, HTTPError
from globalmaptiles import GlobalMercator
from progressbar import *
import subprocess
import multiprocessing 
from PIL import Image
import shutil
import json


def parse_options(config_file):
    params = {
        "level":{
            "value": 16,
            "type": int
        },
        "lon":{
            "value": 102.861464,
            "type": float
        },
        "lat":{
            "value": 24.870115,
            "type": float
        },
        "radius":{
            "value": 3000,
            "type": int
        },
        "google_image_folder":{
            "value": './images',
            "type": unicode
        },
        "key":{
            "value": '',
            "type": unicode
        },
        "out":{
            "value": './out.jpeg',
            "type": unicode
        },
        "map_type":{
            "value": 'satellite',
            "type": unicode
        },
        "format":{
            "value": 'jpg-baseline',
            "type": unicode
        },
        "scale":{
            "value": 1,
            "type": int
        },
        "bottom_crop":{
            "value": 23,
            "type": int
        },
        "resume":{
            "value": False,
            "type": bool
        },
        "debug": {
            "value": False,
            "type": bool
        }

    }

    with open(config_file) as json_data:
        d = json.load(json_data)
        if d is None:
            return None
        for obj in params:
            if obj in d:
                params[obj]["value"] = d[obj]
                if type(d[obj]) is not params[obj]["type"]:
                    print(obj, "type is", params[obj]["type"], "provided is", type(d[obj]))
                    return None
    
        return params


###
# Functions
###
def execute_system_command(command):
    try:
        FNULL = open(os.devnull, 'w')
        retcode = subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode)
            return False
        else:
            return True
    except OSError as e:
        print("Execution failed:", e)
        return False


def dlfile(url, filename):
    # Open the url
    try:
        f = urlopen(url)
        #print "downloading " + url

        # Open our local file for writing
        with open(filename, "wb") as local_file:
            local_file.write(f.read())

        # crop image
        command = 'mogrify -gravity north -extent %dx%d %s' % (actual_tile_size, actual_tile_size, filename)
        os.system(command)

    # handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url


def process_tile(tile_pair):
    tx = tile_pair[0]
    ty = tile_pair[1]

    gtx, gty = mercator.GoogleTile(tx, ty, tz)
    image_file = '%s/%d_%d_%d.jpg' % (google_image_folder, tz, gtx, gty)
    #tif_file = '%s/%d_%d_%d.tif' % (tif_folder, tz, gtx, gty)
    (minLat, minLon, maxLat, maxLon) = mercator.TileLatLonBounds(tx, ty, tz)

    lat = (minLat + maxLat) / 2.0
    lon = (minLon + maxLon) / 2.0
    # download google image
    url_str = 'https://maps.googleapis.com/maps/api/staticmap?maptype=%s&format=%s&scale=%d&center=%f,%f&zoom=%d&size=%dx%d&key=%s' % (map_type, format, scale, float(lat), float(lon), tz, image_size, image_size + bottom_crop, KEY)
    #url_str = 'http://www.google.cn/maps/vt?lyrs=s@739&gl=cn&x=%d&y=%d&z=%d' % (gtx, gty, tz)

    if os.path.exists(image_file) and os.path.getsize(image_file) <= 2000:
        os.remove(image_file)

    if not os.path.exists(image_file):
        dlfile(url_str, image_file)


def debug_print(str):
    if debug:
        print(str)

def merge_images(tile_pair):
    tx = tile_pair[0]
    ty = tile_pair[1]

    gtx, gty = mercator.GoogleTile(tx, ty, tz)
    image_file = '%s/%d_%d_%d.jpg' % (google_image_folder, tz, gtx, gty)

    if not os.path.exists(image_file):
        debug_print("image file not exist: %s" % image_file)
        return

    tile_image = Image.open(image_file)
    px = (gtx - gtx0) * actual_tile_size
    py = new_im.height - (gty0 - gty + 1) * actual_tile_size
    new_im.paste(tile_image, (px, py))


def get_value(params, key):
    if key not in params:
        return None

    return params[key]["value"]

###
# main function
###
if __name__=='__main__': 
    # Parse command line options
    conf_file = './config.json'
    if len(sys.argv) >= 2:
        conf_file = sys.argv[1]
    if not os.path.exists(conf_file):
        print("configure file %s not exist!" % conf_file)
        exit()

    params = parse_options(conf_file)
    if params is None:
        print("parsing configure file fail!")
        exit()

    google_image_folder = get_value(params, "google_image_folder")
    output_jpeg_file = get_value(params, "out")
    map_type = get_value(params, "map_type")
    format = get_value(params, "format")
    tz = get_value(params, "level")
    lon = get_value(params, "lon")
    lat = get_value(params, "lat")
    radius = get_value(params, "radius")
    bottom_crop = get_value(params, "bottom_crop")
    KEY = get_value(params, "key")
    resume = get_value(params, "resume")
    image_size = 256
    scale = get_value(params, "scale")
    debug = get_value(params, "debug")
    if google_image_folder is None or output_jpeg_file is None or map_type is None or format is None or tz is None or lon is None or lat is None or radius is None or bottom_crop is None or KEY is None or image_size is None or scale is None or resume is None or debug is None:
        print("invalid parameter exists!")
        exit()
    actual_tile_size = image_size * scale 
    debug_print("actual tile size %d" % actual_tile_size)

    if not resume:
        if os.path.exists(google_image_folder):
            shutil.rmtree(google_image_folder)
        if os.path.exists(output_jpeg_file):
            os.unlink(output_jpeg_file)

    if not os.path.exists(google_image_folder):
        os.makedirs(google_image_folder)

    mercator = GlobalMercator()
    cx, cy = mercator.LatLonToMeters(lat, lon)
    minx = cx - radius
    maxx = cx +  radius
    miny = cy - radius
    maxy = cy + radius
    debug_print('minx = %f, miny = %f, maxx = %f, maxy = %f\n' % (minx, miny,  maxx, maxy))

    tminx, tminy = mercator.MetersToTile(minx, miny, tz)
    tmaxx, tmaxy = mercator.MetersToTile(maxx, maxy, tz)

    total_tiles = (tmaxx - tminx + 1) * (tmaxy - tminy + 1)
    debug_print('count = %d' % total_tiles)

    # progress bar
    widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=total_tiles).start()

    tile_list = []
    for ty in range(tminy, tmaxy + 1):
        for tx in range(tminx, tmaxx + 1):
            tile_list.append([tx, ty])

    print("Downloading images ...")
    nthreads = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=nthreads)
    for i, _ in enumerate(pool.imap_unordered(process_tile, tile_list), 1):
        pbar.update(i)

    print("merging images ...")
    nthreads = 1
    gtx0, gty0 = mercator.GoogleTile(tminx, tminy, tz)
    debug_print("create image of size: %d, %d" % ((tmaxx - tminx + 1) * actual_tile_size, (tmaxy - tminy + 1) * actual_tile_size))
    new_im = Image.new('RGB', ((tmaxx - tminx + 1) * actual_tile_size, (tmaxy - tminy + 1) * actual_tile_size))
    for tile_pair in tile_list:
        merge_images(tile_pair)

    print("saving ...")
    new_im.save(output_jpeg_file, "JPEG")
    print("finish!")
    # End of main function
# End of program