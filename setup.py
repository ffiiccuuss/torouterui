#!/usr/bin/env python

from setuptools import setup

setup(
    name='torouterui',
    version='0.0',
    long_description=__doc__,
    packages=['torouterui'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'python-augeas',
    ],
    dependancy_links=['https://fedorahosted.org/released/python-augeas/'],
    entry_points = {
        'console_scripts': [
            'torouterui = torouterui.server:main',
         ],
    },
)
