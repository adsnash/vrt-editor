# USAGE

This guide assumes you have a valid VRT created with GDAL - see VRT CREATION section of README.md for more information.

### Instantiation

Import the class and instantiate it with the path to VRT

```python
# import the class
from vrt.edit import VrtEditor

# path to vrt file on disk
# NOTE: this is for a single band VRT
vrt_path_single = 'path/to/single_band.vrt'

# instantiate the class with the vrt path 
vrt1 = VrtEditor(vrt_path_single)
```

### Simple Function

Add a simple function to add 10 to every pixel, then write the edited VRT

The name of the method in `func_str` matches the one added with the `embed_func_string` method 

The method has the proper signature and modifies `out_ar` in place - see PIXEL FUNCTION SIGNATURE in README.md for more info

Since the vrt is single band, the `band` variable of `embed_func_string` does not need to be specified

```python
# string of python pixel function to be embedded
func_str1 = '''
import numpy as np

def add_10(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(np.add(in_ar[0], 10), 0, 255)
'''

# embed the pixel function
# NOTE: the name provided matches the name of the method in the string
vrt1.embed_func_string('add_10', func_str1)

# write the vrt to disk
# NOTE: this should be done whenever the VRT editing is finished
vrt1.write_vrt('add_10.vrt')
```

### Change Datatype

Methods that change the datatype are valid, but the new output datatype must be specified by `new_dtype`

```python
# this method changes the output dataype to float32 
func_str2 = '''
import numpy as np

def test_type_change(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.add(in_ar[0], 6.5, dtype=np.float32)
'''

# embed the pixel function
# NOTE: also setting new_dtype value
vrt1.embed_func_string('test_type_change', func_str2, new_dtype='Float32')
```

### Provide Input Values

You can pass input values (specified outside your pixel function) like so:

```python
# pixel function args retrieved via kwargs required in signature
func_str3 = '''
import numpy as np

def test_input_dict(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	val1 = int(kwargs['val1'])
	val2 = float(kwargs['val2'])
	out_ar[:] = np.add(in_ar[0], val1 + val2, dtype=np.float32)
'''

# dict of values to provide
kwarg_dict = {'val1': '1', 'val2': '2.4'}

# embed the pixel function
# NOTE: use the ** to provide the kwargs in kwarg_dict
vrt1.embed_func_string('test_input_dict', func_str3, new_dtype='Float32', **kwarg_dict)
```

## Multi-band VRT's

Up to this point, all of our examples have been on single-band VRT's. Let's look at how we would work with multi-band VRT's.

NOTE: band numbers are handled the same way as they are handled in GDAL i.e. they are 1-indexed NOT 0-indexed

```python
# import the class, same as before
from vrt.edit import VrtEditor

# path to vrt file on disk
# NOTE: this is for a 3 band VRT
vrt_path_3band = 'path/to/three_band.vrt'

# NOTE: this is for a 4 band VRT
vrt_path_4band = 'path/to/four_band.vrt'

# instantiate for 3 band vrt path 
vrt3 = VrtEditor(vrt_path_3band)

# instantiate for 4 band vrt path 
vrt4 = VrtEditor(vrt_path_4band)
```  

### Add a Different Method to Each Band

Add a simple method to each band, but each method will be DIFFERENT (to confirm that it worked). 

To specify the band to embed the pixel function into, use the `band_num` variable.

NOTE: even if embedding the same method into each band, it would need to be specified on a per-band basis like so

```python
# method for band 1 - adds 10
# NOTE: band 1 is the first band - this is GDAL style
# this would be the zero index of a numpy array 
band_func1 = '''
import numpy as np

def test_multiband_1(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(np.add(in_ar[0], 10), 0, 255)
'''

# embed the pixel function into band 1
vrt3.embed_func_string('test_multiband_1', band_func1, band_num=1)


# method for band 2 - adds 20
band_func2 = '''
import numpy as np

def test_multiband_3(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(np.add(in_ar[0], 20), 0, 255)
'''

# embed the pixel function into band 2
vrt3.embed_func_string('test_multiband_2', band_func2, band_num=2)


# method for band 3 - adds 30
band_func3 = '''
import numpy as np

def test_multiband_3(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(np.add(in_ar[0], 30), 0, 255)
'''

# embed the pixel function into band 3
vrt3.embed_func_string('test_multiband_3', band_func3, band_num=3)
```

### Reorder Bands

Reordering bands is straightforward, call the `reorder_bands` method with a list of ints in the desired order
 
NOTE: make sure to provide values that are 1-indexed

```python
# list of new band order for 3 band image - BGR (swapping bands 1 and 3)
band_order_bgr = [3, 2, 1]

# reorder the bands
vrt3.reorder_bands(band_order_bgr)
```

### Remove Bands

Removing bands is fairly as well straightforward, but can get a little confusing. The `remove_band` method will remove the desired band index, but the remaining bands will shift to fill its place. 

For example, if you remove band 2 of a 3 band image, band 3 becomes band 2 when referencing the band numbers.

As such, it is recommended to reorder bands before removing them - moving the band(s) to be removed to the end. When removing multiple bands, remove the highest index first. This is not required but will help avoid confusion

```python
# removing bands 2 and 3 of a 3 band VRT the recommended way (reverse order)
vrt4.remove_band(band_num=3)
vrt4.remove_band(band_num=2)

# removing bands 2 and 3 the NOT recommended way (remove band 2 twice, since band 3 becomes band 2 when band 2 is removed)
vrt4.remove_band(band_num=2)
vrt4.remove_band(band_num=2)

# this will FAIL
vrt4.remove_band(band_num=2)
vrt4.remove_band(band_num=3)  # this line fails
```

### Common Workflow - CIR

With the `reorder_bands` and `remove_band` method, this will create a color infrared (CIR) image from our 4 band VRT

```python
# list of new band order, setting the band to be removed last
cir_band_order = [4, 1, 2, 3]

# reorder the bands
vrt4.reorder_bands(cir_band_order)

# the old third band (now the fourth band) is removed 
vrt4.remove_band(band_num=4)
```

### Multi-band Functions

It is possible to create pixel functions that utilize multiple bands as input (but still operate on a per-band basis)

The next example demonstrates how to add two bands together, in this case bands 1 and 3. They are accessed by `in_ar` in the order that they were added. 

In order for band 1 to have access to have access to band 3, the band 3 source is first accessed with `get_band_source` and then added to band 1 with `add_band_source`

NOTE: the pixel function is added only to band 1 - bands 2 and 3 will remain unchanged

```python
# extract the desired band source (band 3)
band_3_src = vrt4.get_band_source(3)

# add the band source to the destination band (band 1)
vrt4.add_band_source(band_3_src, band_num=1)

# add them together
# NOTE: bands are accessed by in_ar in the order they were added
combine_bands_str = '''
import numpy as np

def test_combinebands(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	out_ar[:] = np.clip(in_ar[0] + in_ar[1], 0, 255)
'''

# embed the pixel function
# NOTE: embedding into the same band that the extra source was added to
vrt4.embed_func_string('test_combine_bands', combine_bands_str, band_num=1)
```

### Common Workflow - NDVI

Here is an example workflow for a classic GIS task - calculating NDVI

```python
# method to calculate NDVI
ndvi_str = '''
import numpy as np

np.seterr(divide='ignore',invalid='ignore')

def test_ndvi(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
	red = in_ar[0].astype(np.float32)
	nir = in_ar[1].astype(np.float32)
	num = nir - red
	den = nir + red
	out_ar[:] = np.clip(((np.nan_to_num(num / den)+1)*127.5), 0, 255).astype(np.int8)
'''

# add the pixel function to band 1 - red band
vrt4.embed_func_string('test_ndvi', ndvi_str, band_num=1)

# add the band source for band 4 (NIR) to band 1
vrt4.add_band_source(vrt4.get_band_source(4), band_num=1)

# remove the remaining bands
# NOTE: deleting bands in reverse order to avoid any complications
# alternatively, for this example, calling vrt4.remove_band(band_num=2) three times would produce the same outcome
vrt4.remove_band(band_num=4)
vrt4.remove_band(band_num=3)
vrt4.remove_band(band_num=2)
```

### Using Files From Disk

So far all the examples for embedding pixel functions have used string of python methods. However, it is also possible to use python modules in separate files. 

NOTE: make sure the module is discoverable by putting it on the PYTHONPATH. See "ModuleNotFoundError" WHEN USING FILE section of README.md

```python
# in this example, the desired file is 'file_name.py' 
# the desired method in file_name.py (which still has the proper signature) is 'file_method'
vrt3.embed_func_module('file_method', 'file_name.file_method', band_num=1)
```

### Hillshade Example

One of the examples in the official GDAL VRT documentation is hillshading. The code for the hillshade method can be found here: https://gdal.org/drivers/raster/vrt.html#vrt-that-computes-hillshading-using-an-external-library

This example shows how it would be embedded via the VRT editor

```python
vrt1.embed_func_module('hillshade', 'test_dir.hillshading', buffer_radius=1, **{'scale':'111120', 'z_factor': '30'})
```

### Numba Example

Another one of the examples 

in the official GDAL VRT documentation is mandelbrot using Numba. The code for the mandelbrot method can be found here: https://gdal.org/drivers/raster/vrt.html#just-in-time-compilation

When looking at the code, notice the setup - there's a wrapper method that is specified in the edited VRT which has the proper signature. It calls an interior method which has the Numba jit decorator - this is how a Numba accelerated pixel function needs to be setup. 

Obviously, in order to use Numba, Numba must be installed as a requirement.  

This example shows how it would be embedded via the VRT editor

```python
vrt1.embed_func_module('mandelbrot', 'mandelbrot.mandelbrot')
```

