# VRT Editor

VRT's are XML representations of a raster images. They are an extremely useful tool that can provide a lot of lift to the GIS/GDAL power user. You can read more about them here: https://gdal.org/drivers/raster/vrt.html or view the schema here: https://raw.githubusercontent.com/OSGeo/gdal/master/gdal/data/gdalvrt.xsd 

A little known fact about them is that they support embedded pixel functions. These functions, written in python, can be embedded directly into the VRT and will be executed when the VRT is transformed into a tif with the `gdal_translate` command.

This class is designed to edit VRT's, allowing a user to reorder/remove bands and embed pixel functions. These pixel functions can be strings of valid python or files on disk, so long as they have the proper signature. 

NOTE: the code works for editing VRT's that have been build with GDAL 2 and 3.

## INSTALLATION

To install directly, clone this repo and run the setup.py

```
# clone the repo
git clone https://github.com/adsnash/vrt-editor.git

# get inside the repo directory
cd vrt-editor

# run setup.py
python3 setup.py install
```

Alternatively, you can use the Dockerfile - more information in the DOCKER section below.

## PIXEL FUNCTION SIGNATURE

The signature of a valid pixel function is defined in the docs here: https://gdal.org/drivers/raster/vrt.html#using-derived-bands-with-pixel-functions-in-python

The relevant section has been pasted below:


    The signature of the Python pixel function must have the following arguments:

    in_ar: list of input NumPy arrays (one NumPy array for each source)

    out_ar: output NumPy array to fill. The array is initialized at the right dimensions and with the VRTRasterBand.dataType.

    xoff: pixel offset to the top left corner of the accessed region of the band. Generally not needed except if the processing depends on the pixel position in the raster.

    yoff line offset to the top left corner of the accessed region of the band. Generally not needed.

    xsize: width of the region of the accessed region of the band. Can be used together with out_ar.shape[1] to determine the horizontal resampling ratio of the request.

    ysize: height of the region of the accessed region of the band. Can be used together with out_ar.shape[0] to determine the vertical resampling ratio of the request.

    raster_xsize: total with of the raster band. Generally not needed.

    raster_ysize: total with of the raster band. Generally not needed.

    buf_radius: radius of the buffer (in pixels) added to the left, right, top and bottom of in_ar / out_ar. This is the value of the optional BufferRadius element that can be set so that the original pixel request is extended by a given amount of pixels.

    gt: geotransform. Array of 6 double values.

    kwargs: dictionary with user arguments defined in PixelFunctionArguments
    
    The provided out_ar array must be modified in-place. Any value currently returned by the pixel function is ignored.

### NOTES ON PIXEL FUNCTIONS

It is important to note that while these arguments are requirements for a valid pixel function, they do not need to be used. 

Below is an example of a simple pixel function that adds to 10 every pixel in an image, then clips its value range to stay within that of uint8:

```python
import numpy as np

def test_simple(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(np.add(in_ar[0], 10), 0, 255)
```

Another note to be aware of is that `in_ar` is a _list_ of arrays, even if only one array is present, while `out_ar` is a single array that must be modified in place. The list of arrays in `in_ar` is in the order that they were added to the VRT.

It is also important to note that the processing of images happens in blocks - this means that pixel functions that don't operate on a strictly per-pixel basis (such as setting pixel values based on the histogram of all the pixels in `in_ar`) will likely produce undesired results. Depending on the functionality, it may be possible to mitigate the issue by providing kwarg arguments, but any sort of function that requires ALL of the pixels in the entire image will not produce the correct results.

Finally, please note that there is currently NO validation of user input - it is on you to properly create these python functions.

## VRT CREATION

To create a VRT, use the GDAL cli method `gdalbuildvrt` or the python api's `gdal.BuildVRT` method. The docs are available here: https://gdal.org/programs/gdalbuildvrt.html

Please note, a VRT can NOT be created from ungeoreferenced images.

An example command creating a VRT from a single image via the cli:

```
gdalbuildvrt test.vrt image.tif
```

The same VRT can be built with the python api like so:

```python
from osgeo import gdal

gdal.BuildVRT('test.vrt', 'image.tif')
```

### NOTE ON PATHS

Providing relative paths to tif(s) when calling `gdalbuildvrt` from the cli (or `gdal.BuildVRT` via python) will create a valid VRT. However, the VRT will becoming invalid if the relative path of either it or the asset(s) that created it change. This includes writing a new VRT - if using relative paths, it MUST be in the same location as the original VRT. It is possible to circumvent these issues by using absolute paths.

### NOTE ON MULTIPLE IMAGES

It is possible to create a single VRT for multiple images, such as with: 

```
gdalbuildvrt multi.vrt img1.tif img2.tif img3.tif
```

However, multi-image VRT's are currently NOT fully supported. Some methods will work properly, others will have unexpected outputs.


## USAGE

See USAGE.md


## PRODUCING AN IMAGE

In order to actually create an image from the edited VRT, use `gdal_translate` with the flag "--config GDAL_VRT_ENABLE_PYTHON YES" like so:

```
gdal_translate edited.vrt final.tif --config GDAL_VRT_ENABLE_PYTHON YES
```

The documentation on `gdal_translate` can be found here: https://gdal.org/programs/gdal_translate.html

Note that the rest of the `gdal_translate` options can be used in the same call to create the output tif.

The documentation on this config option (and its security concerns) can be found here: https://gdal.org/drivers/raster/vrt.html#security-implications	docs on the config option: https://gdal.org/drivers/raster/vrt.html#security-implications

### ENSURE CORRECT PYTHON VERSION

For whatever reason, GDAL will first try to use python2. To ensure the correct python is used, set the variable `PYTHONSO` to the path to the desired python's .so/.dylib/.dll (depending on your system). On my mac, that looks like:

```
export PYTHONSO=/usr/local/Cellar/python/3.7.6_1/Frameworks/Python.framework/Versions/3.7/lib/libpython3.7.dylib
```

To check the version of python being used, when running `gdal_translate`, add the extra config option `--config CPL_DEBUG ON` like so:

```
gdal_translate edited.vrt final.tif --config GDAL_VRT_ENABLE_PYTHON YES --config CPL_DEBUG ON
```

Read the documentation about this issue here: https://gdal.org/drivers/raster/vrt.html#linking-mechanism-to-a-python-interpreter and check out this post: https://github.com/OSGeo/gdal/issues/1660
	
### "ModuleNotFoundError" WHEN USING FILE

This error comes from python being unable to find your module, and can be easily fixed by adding it to your `PYTHONPATH`, like so:

```
export PYTHONPATH=/path/to/my/module
```

Make sure to include a `__init__.py` in the module directory.

Read the documentation about this issue here: https://gdal.org/drivers/raster/vrt.html#python-module-path


## REQUIREMENTS

It is assumed that the user has GDAL installed on their machine, as GDAL is required to build a VRT and create an image from it, but it is not an explicit requirement for this code to run.

The only third party libraries required are `xmltodict` and `numpy` - ideally the same version of numpy that your GDAL was built with but that is not a hard requirement.

Numba is only a requirement if you plan to use it, but since there is a test case using it, it is added as a requirement. This can be removed if desired.

As of writing (7/15/2020), my versions of these libraries are:

```
xmltodict==0.12.0
numpy==1.19.0
numba==0.50.1
pytest==5.4.3
```

Newer versions will almost certainly work. Older versions may work as well, but are not guaranteed to work. 

## DOCKER

See DOCKER_NOTES.md for full guide, here's the tl;dr

### Build the container

```
docker build -t vrt_editor .
```

### Run the Container

```
docker run -it -v $PWD:/app vrt_editor bash
```

## MOTIVATION

I initially wrote this code when I needed a fast way to calculate top of atmosphere reflectance on a large amount of raw satellite swaths (which had been provided in their rawest format). Even just opening the images in memory (which were tens of thousands by tens of thousands of pixels) took ages. I needed a better solution - enter VRT pixel functions.

GDAL's VRT page is a fantastic resource, but it did not exist in its current incarnation at the time when I first wrote this code. Instead, I had to work largely off Even's post here: https://lists.osgeo.org/pipermail/gdal-dev/2016-September/045134.html

I began experimenting with editing VRT's by hand. However, the top of atmosphere reflectance calculation requires a number of variables (such as sun azimuth) that change for every single swath, and I had a few hundred swaths to do. 

I wrote this code to be extensible beyond just my own use case. I hope it can be useful to anyone who needs to perform fast pixel-wise calculations on a raster.


## TODO

See TODO.md

