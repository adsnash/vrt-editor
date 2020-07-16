#!/usr/bin/env python3

import os
import io
from setuptools import setup, find_packages

setup(
      name='vrt',
      version="0.1",
      description="Edit GDAL VRT's - embed pixel function, reorder, and remove bands",
      url='https://github.com/adsnash/vrt_editor',
      author='Alex Nash',
      author_email='anash@protonmail.com',
      license='MIT',
      dependency_links=[],
      packages=find_packages(exclude=["contrib", "docs", "tests"]),
      include_package_data=True,
      python_requires=">=3.6, <4",
      install_requires=[
            "numba>=0.50.1",
            "numpy>=1.19.0",
            "pytest==5.4.3",
            "xmltodict>=0.12.0",
      ],
      zip_safe=False
)
