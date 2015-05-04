#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(name='eh_file_manager',
        version='0.4',
        description='File managment system that can be used as off-line version of e-hentai.org gallery system.',
        long_description=open("README.md").read(),
        author='Jiří Kuneš',
        author_email='jirka642@gmail.com',
        url='https://github.com/kunesj/EH-file-manager',
        packages=['ehfilemanager'],
        include_package_data=True,
        license="GPL2",
        entry_points={
        'console_scripts': ['ehfilemanager = ehfilemanager.ehfm_application:main'],
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
