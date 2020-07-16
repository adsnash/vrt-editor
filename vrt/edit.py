import xmltodict
import collections
import numpy as np


# list of gdal data types
gdal_data_types = ["Byte", "UInt16", "Int16", "UInt32", "Int32", "Float32", "Float64", "CInt16", "CInt32", "CFloat32", "CFloat64"]

# mapping of gdal data types to numpy data types
np_gdal_dict = {np.uint8: 'Byte', np.uint16: 'UInt16', np.int16: 'Int16', np.uint32: 'UInt32', np.int32: 'Int32', np.float32: 'Float32', np.float64: 'Float64'}

 
class VrtEditor:
	"""
	class to edit a gdal VRT - an XML representation of a raster image
	allows for reordering/removeal of bands and embedding pixel functions
	docs on VRT's: https://gdal.org/drivers/raster/vrt.html
	pixel functions can be python strings or files from disk
	the provided pixel function MUST have the proper signature
	docs on function signature: https://gdal.org/drivers/raster/vrt.html#using-derived-bands-with-pixel-functions-in-python
	to create a VRT, use the gdal cli method gdalbuildvrt or the python api's gdal.BuildVRT
	docs on build VRT's: https://gdal.org/programs/gdalbuildvrt.html
	for info on how to use this class, checkout the README.md and the test cases
	to actually create an image from the edited VRT, use gdal_translate with "--config GDAL_VRT_ENABLE_PYTHON YES", ex:
	gdal_translate in.vrt out.tif --config GDAL_VRT_ENABLE_PYTHON YES
	docs on gdal_translate: https://gdal.org/programs/gdal_translate.html
	docs on the config option: https://gdal.org/drivers/raster/vrt.html#security-implications
	"""
	def __init__(self, in_vrt_path):
		self.in_path = in_vrt_path
		self.vrt_dict = self._read_vrt(in_vrt_path)
		self.num_bands = 0
		self._determine_num_bands()
		self.embed_band = None

	def _read_vrt(self, in_vrt_path):
		"""
		open vrt and return ordered json dict created with xmltodict library
		"""
		with open(in_vrt_path) as file_reader:
			return xmltodict.parse(file_reader.read())

	def write_vrt(self, out_vrt_path):
		"""
		write vrt dict to .vrt file
		NOTE: need to check that path is valid and ends in .vrt
		"""
		# remove standard xml starting line '<?xml version="1.0" encoding="utf-8"?>'
		# NOTE: removing this is NOT necessary for it to work, but makes output standardized vrt
		out_vrt_string = '\n'.join(xmltodict.unparse(self.vrt_dict, pretty=True).split('\n')[1:])
		with open(out_vrt_path, 'w') as file_writer:
			file_writer.write(out_vrt_string)

	def _determine_num_bands(self):
		"""
		determine the number of bands in the vrt (single band is different from multiband)
		"""
		if type(self.vrt_dict['VRTDataset']['VRTRasterBand']) == list:
			self.num_bands = len(self.vrt_dict['VRTDataset']['VRTRasterBand'])
		# handle for single band
		else:
			self.num_bands = 1
		return

	def _update_ordered_dict(self, ordered_dict, input_dict_list, key_add_after):
		"""
		method to update an ordered dict given input dict list and desired key to add values after
		NOTE: key_add_after is the key to add input_dict after (everything AFTER that will be shifted back)
		"""
		new_dict = ordered_dict.copy()
		key_list = list(new_dict.keys())
		pop_keys = key_list[key_list.index(key_add_after)+1: ]
		pop_dict_list = input_dict_list + [{key: new_dict.pop(key)} for key in pop_keys]
		for key_val_dict in pop_dict_list:
			new_dict.update(key_val_dict)
		return new_dict

	def embed_func_string(self, method_name, python_string, band_num=0, buffer_radius=0, new_dtype='', **kwargs):
		"""
		high level method to embed the string of a python function into a band
		NOTE: the main method called (method_name) MUST have the correct signature and modify out_ar in place
		docs: https://gdal.org/drivers/raster/vrt.html#using-derived-bands-with-pixel-functions-in-python
		"""
		self.embed_band = self._get_band_dict(band_num)
		self._add_function(method_name, python_string, buffer_radius, new_dtype, **kwargs)
		if band_num > 0:
			# NOTE: subtract one since gdal bands are 1-indexed
			self.vrt_dict['VRTDataset']['VRTRasterBand'][band_num - 1] = self.embed_band
		elif band_num == 0:
			self.vrt_dict['VRTDataset']['VRTRasterBand'] = self.embed_band
		return

	def embed_func_module(self, method_name, python_module, band_num=0, buffer_radius=0, new_dtype='', **kwargs):
		"""
		high level method to embed the a python file function into a band
		NOTE: the main method called (method_name) MUST have the correct signature and modify out_ar in place
		docs: https://gdal.org/drivers/raster/vrt.html#using-derived-bands-with-pixel-functions-in-python
		NOTE: python_module MUST be in proper import format AND discoverable via PYTHONPATH 
		docs: https://gdal.org/drivers/raster/vrt.html#python-module-path
		"""
		# setup module method path - 
		module_method = '.'.join([python_module, method_name])
		self.embed_band = self._get_band_dict(band_num)
		self._add_function(module_method, '', buffer_radius, new_dtype, **kwargs)
		if band_num > 0:
			# NOTE: subtract one since gdal bands are 1-indexed
			self.vrt_dict['VRTDataset']['VRTRasterBand'][band_num - 1] = self.embed_band
		elif band_num == 0:
			self.vrt_dict['VRTDataset']['VRTRasterBand'] = self.embed_band
		return

	def _get_band_dict(self, band_num):
		"""
		get dict of band by index
		"""
		# ensure bands haven't changed
		self._determine_num_bands()
		# handle for multi-band vrt - positive band_num and num_bands
		# ASSUMPTION: self.num_bands will NEVER be 1 and have a nested list 
		# TODO: ensure this is true for multi-tif, single band vrt
		if band_num > 0 and self.num_bands > 1:
			# NOTE: subtract one since gdal bands are 1-indexed
			return self.vrt_dict['VRTDataset']['VRTRasterBand'][band_num - 1]
		# handle for single-band vrt - band_num should be 0
		elif band_num == 0 and self.num_bands == 1:
			return self.vrt_dict['VRTDataset']['VRTRasterBand']
		# raise error for user error - custom error message?
		raise ValueError('Bad band input value')

	def _add_function(self, method_or_module, python_string='', buffer_radius=0, new_dtype='', **kwargs):
		"""
		interior method to embed a python function (as a string or file) into a band 
		NOTE: if using a file, method_or_module MUST be properly formatted
		ASSUMPTION: input dictionary does NOT alreay have an embedded pixel function
		"""
		components = [{'@subClass': 'VRTDerivedRasterBand'}, {'PixelFunctionType': method_or_module}, {'PixelFunctionLanguage': 'Python'}]
		if len(kwargs.keys()) > 0:
			components.append({'PixelFunctionArguments': self._prep_kwargs(**kwargs)})
		# only add 'PixelFunctionCode' if embedding a string
		# ASSUMPTION: module has been properly formatted
		if python_string != '':
			# ASSUMPTION: python string is valid and will work - not currently error checking
			components.append({'PixelFunctionCode': python_string})
		# add buffer radius if provided
		# TODO: determine what happens if negative values provided
		if buffer_radius > 0:
			components.append({'BufferRadius': buffer_radius})
		if new_dtype != '':
			# make sure input datatype is valid and supported
			new_datatype = self._confirm_datatype(new_dtype)
			self.embed_band['@dataType'] = new_datatype
			components.append({'SourceTransferType': new_datatype})
		# add pixel function components to ordered dict
		self.embed_band = self._update_ordered_dict(self.embed_band, components, '@band')
		return 

	def _prep_kwargs(self, **kwargs):
		"""
		make ordered dict of input kwargs
		NOTE: keys begin with @ and values are strings 
		"""
		key_list = ['@'+str(key) for key in kwargs.keys()]
		val_list = [str(val) for key, val in kwargs.items()]
		return collections.OrderedDict(zip(key_list, val_list))

	def _confirm_datatype(self, new_dtype):
		"""
		confirm that datatype is valid and supported
		handles for gdal AND np datatypes, converts np to gdal datatypes
		"""
		if new_dtype in gdal_data_types:
			return new_dtype
		elif new_dtype in np_gdal_dict:
			return np_gdal_dict[new_dtype]
		raise ValueError('Bad input data type')

	### multi-band methods ###

	def get_band_source(self, band_num=0):
		"""
		wrapper to _band_source to allow user to pass a band number
		ASSUMPTION: band in question will ONLY have 1 band source (i.e. won't work if additional source has already been added)
		"""
		return self._band_source(self._get_band_dict(band_num))

	def _band_source(self, band):
		"""
		get band type and band source from a band dict
		NOTE: band types supported include 'SimpleSource' and 'ComplexSource'
		"""
		if 'SimpleSource' in band.keys():
			band_type = 'SimpleSource'
		elif 'ComplexSource' in band.keys():
			band_type = 'ComplexSource'
		else:
			raise ValueError(f"Could not pull band source for band number {band_num}, only 'SimpleSource' and 'ComplexSource' currently supported")
		band_src = band[band_type]
		if type(band_src) != list:
			band_src = [band_src]
		return {'band_type': band_type, 'band_src': band_src}

	def add_band_source(self, add_band_src, band_num=0):
		"""
		add a band source to a band by index 
		allows for methods involving multiple bands
		"""
		self.embed_band = self._get_band_dict(band_num)
		band_dest = self._band_source(self.embed_band)
		if band_dest['band_type'] == add_band_src['band_type']:
			self.embed_band[band_dest['band_type']] = band_dest['band_src'] + add_band_src['band_src']
		# handle for different source types (simple vs complex)
		else:
			# handle for single input from source band
			if len(add_band_src['band_src']) == 1:
				add_band_src['band_src'] = add_band_src['band_src'][0]
			self.embed_band.update({add_band_src['band_type']: add_band_src['band_src']})
		if band_num > 0:
			# NOTE: subtract one since gdal bands are 1-indexed
			self.vrt_dict['VRTDataset']['VRTRasterBand'][band_num - 1] = self.embed_band
		elif band_num == 0:
			self.vrt_dict['VRTDataset']['VRTRasterBand'] = self.embed_band
		return

	def remove_band(self, band_num=0):
		"""
		remove a band index not desired in final output image
		NOTE: will NOT remove band if only 1 exists
		"""
		self._determine_num_bands()
		if band_num == 0 and self.num_bands == 1:
			raise ValueError('Can not remove band, only 1 band remains')
		elif band_num > self.num_bands:
			raise ValueError('Remove_band index {} higher than number of VRT bands {}'.format(band_num, self.num_bands))
		elif band_num > 0 and self.num_bands > 1:
			# NOTE: subtract one since gdal bands are 1-indexed
			_ = self.vrt_dict['VRTDataset']['VRTRasterBand'].pop(band_num - 1)
			self._determine_num_bands()
			# handle for only 1 remaining band - single-entry list 
			if self.num_bands == 1:
				self.vrt_dict['VRTDataset']['VRTRasterBand'] = self.vrt_dict['VRTDataset']['VRTRasterBand'][0]
			self._determine_num_bands()
			return
		else:
			raise ValueError('Bad band number provided')

	def reorder_bands(self, band_order_list):
		"""
		reorder bands based on input list
		"""
		self._determine_num_bands()
		if len(band_order_list) != self.num_bands:
			raise ValueError('Invalid band order list')
		new_band_order = [self.vrt_dict['VRTDataset']['VRTRasterBand'][band - 1] for band in band_order_list]
		for i, band in enumerate(new_band_order):
			band['@band'] = i+1
		self.vrt_dict['VRTDataset']['VRTRasterBand'] = new_band_order
		return
		


