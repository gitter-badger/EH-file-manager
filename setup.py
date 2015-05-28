#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup
from os.path import *

import ehfilemanager

setup(name='ehfilemanager',
        version=ehfilemanager.__version__,
        description='File managment system that can be used as off-line version of e-hentai.org gallery system.',
        long_description= open(join(dirname(__file__), 'README.md')).read(),
        author='Jiří Kuneš',
        author_email='jirka642@gmail.com',
        url='https://github.com/kunesj/EH-file-manager',
        download_url = 'https://github.com/kunesj/EH-file-manager/tarball/v'+str(ehfilemanager.__version__),
        keywords = ['manga'],
        packages=['ehfilemanager'],
        include_package_data=True,
        license="GPL2",
        entry_points={
        'console_scripts': ['ehfilemanager = ehfilemanager.ehfm_application:main'],
        #'gui_scripts': ['ehfilemanager_gui = ehfilemanager.ehfm_application:main'],
        },
        install_requires=[
          'beautifulsoup',
          'requests',
          'pylzma',
          'rarfile',
          'pyyaml',
          'pysqlite',
          'python-dateutil'
          # python-imaging
          # python-qt4 
        ],
    )
