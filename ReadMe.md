# STATIC-GOOGLEMAP-DOWNLOADER

Static-GoogleMap-Downloader can download google map images tiles and stiching them together to a big image.


## Usage

```bash
python app.py [config.json]
```

## configure file options

```json
{
    "level": 16,
    "lon": 118.620512,
    "lat": 27.874906,
    "radius": 1000,
    "key": "YOU-GOOGLE-STATIC_MAP_KEY",
    "out": "out.jpeg",
    "map_type": "satellite",
    "format": "jpg-baseline",
    "scale": 1,
    "resume": false,
    "debug": true
}
```

* level

    Same as google map level, range 0 to 19.

* lon, lat, radius

    Specify area center and radius, the unit of radius is meter.

* key

    You google static map secrect key, you can apply one [here](https://code.google.com/apis/console).

* out

    Output image file path.

* map_type

    Map type, could be roadmap/satellite/hybird/terrain.

* format

    Output image format, could be png8/png/png32/gif/jpg/jpg-baseline.

* scale

    The factor to scale output image, could be 1 or 2.

* resume

    Resume downloading or not.

* debug

    Print extra debug information.