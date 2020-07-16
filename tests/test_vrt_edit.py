import os
import pytest
import filecmp
from vrt.edit import VrtEditor


# switch for whether to keep edited VRT's created by tests
keep_files = False

# directory of test files
test_dir = 'tests/samples'

# path to vrt file on disk - 1 band
vrt_path_1band = os.path.join(test_dir, 'naip_hermosa_clip_1band.vrt')

# path to vrt file on disk - 3 band
vrt_path_3band = os.path.join(test_dir, 'naip_hermosa_clip_3band.vrt')

# path to vrt file on disk - 4 band
vrt_path_4band = os.path.join(test_dir, 'naip_hermosa_clip_4band.vrt')


### Simple Function

def test_simple():
	out_name = os.path.join(test_dir, 'add_10.vrt')
	vrt1 = VrtEditor(vrt_path_1band)
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
	vrt1.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_1band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Change Datatype

def test_type_change():
	out_name = os.path.join(test_dir, 'type_change.vrt')
	vrt2 = VrtEditor(vrt_path_1band)
	# this method changes the output dataype to float32 
	func_str2 = '''
	import numpy as np

	def test_type_change(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		out_ar[:] = np.add(in_ar[0], 6.5, dtype=np.float32)
	'''
	# embed the pixel function
	# NOTE: also setting new_dtype value
	vrt2.embed_func_string('test_type_change', func_str2, new_dtype='Float32')
	# write the vrt to disk
	vrt2.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_1band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Provide Input Values

def test_input_dict():
	out_name = os.path.join(test_dir, 'input_dict.vrt')
	vrt3 = VrtEditor(vrt_path_1band)
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
	vrt3.embed_func_string('test_input_dict', func_str3, new_dtype='Float32', **kwarg_dict)
	# write the vrt to disk
	vrt3.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_1band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


## Multi-band VRT's

### Add a Different Method to Each Band

def test_multiband():
	out_name = os.path.join(test_dir, 'multiband.vrt')
	vrt4 = VrtEditor(vrt_path_3band)
	# method for band 1 - adds 10
	# NOTE: band 1 is the first band - this is GDAL style
	# this would be the zero index of a numpy array 
	band_func1 = '''
	import numpy as np

	def test_multiband_1(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		out_ar[:] = np.clip(np.add(in_ar[0], 10), 0, 255)
	'''
	# embed the pixel function into band 1
	vrt4.embed_func_string('test_multiband_1', band_func1, band_num=1)
	# method for band 2 - adds 20
	band_func2 = '''
	import numpy as np

	def test_multiband_3(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		out_ar[:] = np.clip(np.add(in_ar[0], 20), 0, 255)
	'''
	# embed the pixel function into band 2
	vrt4.embed_func_string('test_multiband_2', band_func2, band_num=2)
	# method for band 3 - adds 30
	band_func3 = '''
	import numpy as np

	def test_multiband_3(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		out_ar[:] = np.clip(np.add(in_ar[0], 30), 0, 255)
	'''
	# embed the pixel function into band 3
	vrt4.embed_func_string('test_multiband_3', band_func3, band_num=3)
	# write the vrt to disk
	vrt4.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_3band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Reorder Bands

def test_reorder_bands():
	out_name = os.path.join(test_dir, 'reorder_bands.vrt')
	vrt5 = VrtEditor(vrt_path_3band)
	# list of new band order for 3 band image - BGR (swapping bands 1 and 3)
	band_order_bgr = [3, 2, 1]
	# reorder the bands
	vrt5.reorder_bands(band_order_bgr)
	# write the vrt to disk
	vrt5.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_3band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Remove Bands

def test_remove_bands():
	out_name1 = os.path.join(test_dir, 'remove_bands_v1.vrt')
	out_name2 = os.path.join(test_dir, 'remove_bands_v2.vrt')
	vrt6 = VrtEditor(vrt_path_3band)
	vrt7 = VrtEditor(vrt_path_3band)
	vrt8 = VrtEditor(vrt_path_3band)
	# v1 - removing bands 2 and 3 of a 3 band VRT the recommended way (reverse order)
	vrt6.remove_band(band_num=3)
	vrt6.remove_band(band_num=2)
	# write the vrt to disk
	vrt6.write_vrt(out_name1)
	# ensure the new file was written
	assert os.path.exists(out_name1)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_3band, out_name1)
	# v2 - removing bands 2 and 3 the NOT recommended way (remove band 2 twice, since band 3 becomes band 2 when band 2 is removed)
	vrt7.remove_band(band_num=2)
	vrt7.remove_band(band_num=2)
	# write the vrt to disk
	vrt7.write_vrt(out_name2)
	# ensure the new file was written
	assert os.path.exists(out_name2)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_3band, out_name2)
	# ensure it failes properly
	vrt8.remove_band(band_num=2)
	with pytest.raises(ValueError):
		vrt8.remove_band(band_num=3) 
	# remove file created if desired
	if not keep_files:
		os.remove(out_name1)
		os.remove(out_name2)


### Common Workflow - CIR

def test_cir():
	out_name = os.path.join(test_dir, 'cir.vrt')
	vrt10 = VrtEditor(vrt_path_4band)
	# list of new band order, setting the band to be removed last
	cir_band_order = [4, 1, 2, 3]
	# reorder the bands
	vrt10.reorder_bands(cir_band_order)
	# the old third band (now the fourth band) is removed 
	vrt10.remove_band(band_num=4)
	# write the vrt to disk
	vrt10.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_3band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Multi-band Functions

def test_combine_bands():
	out_name = os.path.join(test_dir, 'combine_bands.vrt')
	vrt11 = VrtEditor(vrt_path_4band)
	# extract the desired band source (band 3)
	band_3_src = vrt11.get_band_source(3)
	# add the band source to the destination band (band 1)
	vrt11.add_band_source(band_3_src, band_num=1)
	# add them together
	# NOTE: bands are accessed by in_ar in the order they were added
	combine_bands_str = '''
	import numpy as np

	def test_combinebands(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		out_ar[:] = np.clip(in_ar[0] + in_ar[1], 0, 255)
	'''
	# embed the pixel function
	# NOTE: embedding into the same band that the extra source was added to
	vrt11.embed_func_string('test_combine_bands', combine_bands_str, band_num=1)
	# write the vrt to disk
	vrt11.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_4band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Common Workflow - NDVI

def test_ndvi():
	out_name = os.path.join(test_dir, 'ndvi.vrt')
	vrt12 = VrtEditor(vrt_path_4band)
	# method to calculate NDVI
	ndvi_str = '''
	import numpy as np

	np.seterr(divide='ignore',invalid='ignore')

	def calc_ndvi(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
		red = in_ar[0].astype(np.float32)
		nir = in_ar[1].astype(np.float32)
		num = nir - red
		den = nir + red
		out_ar[:] = np.clip(((np.nan_to_num(num / den)+1)*127.5), 0, 255).astype(np.int8)
	'''
	# add the pixel function to band 1 - red band
	vrt12.embed_func_string('calc_ndvi', ndvi_str, band_num=1)
	# add the band source for band 4 (NIR) to band 1
	vrt12.add_band_source(vrt12.get_band_source(4), band_num=1)
	# remove the remaining bands
	# NOTE: deleting bands in reverse order to avoid any complications
	# alternatively, for this example, calling vrt4.remove_band(band_num=2) three times would produce the same outcome
	vrt12.remove_band(band_num=4)
	vrt12.remove_band(band_num=3)
	vrt12.remove_band(band_num=2)
	# write the vrt to disk
	vrt12.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_4band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Hillshade Example

def test_hillshade():
	out_name = os.path.join(test_dir, 'hillshade.vrt')
	vrt13 = VrtEditor(vrt_path_1band)
	# NOTE: the file hillshading.py has method hillshade
	vrt13.embed_func_module('hillshade', 'hillshading', buffer_radius=1, **{'scale': '111120', 'z_factor': '30'})
	# write the vrt to disk
	vrt13.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_1band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)


### Numba Example

def test_numba():
	out_name = os.path.join(test_dir, 'mandelbrot.vrt')
	vrt14 = VrtEditor(vrt_path_1band)
	# NOTE: the file mandelbrot_code.py has method mandelbrot
	vrt14.embed_func_module('mandelbrot', 'mandelbrot_code')
	# write the vrt to disk
	vrt14.write_vrt(out_name)
	# ensure the new file was written
	assert os.path.exists(out_name)
	# ensure new file HAS been edited
	filecmp.cmp(vrt_path_1band, out_name)
	# remove file created if desired
	if not keep_files:
		os.remove(out_name)

