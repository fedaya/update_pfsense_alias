#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# netsoins_route
# Copyright (C) 2018  Etienne Gille
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from distutils.core import setup as du_setup
from pkg_resources import Requirement, resource_filename
import shutil
import os
import sys

setup(
    name='update_pfsense_alias',
    version='0.1',
    packages=find_packages(),
    url='',
    license='GPL v3.0',
    author='Etienne Gille',
    author_email='etienne.gille@ville-acigne.fr',
    description='Dynamically gets some IP address(es) from addresses to update an alias in pfsense using FauxAPI',
    install_requires=['dnspython', 'Requests'],
    setup_requires=['dnspython', 'Requests'],
    entry_points={
        'console_scripts': [
            'update_pfsense_alias = update_pfsense_alias.__main__:main',
        ],
    },
    package_data={
        'ini_file': [
            'etc/update_pfsense_alias/update_pfsense_alias.ini'
        ]
    },
    include_package_data=True,
)

#u_setup(i
#   name='update_pfsense_alias',
#   data_files=[('/etc/update_pfsense_alias', ['etc/update_pfsense_alias/update_pfsense_alias.ini'])]
#
if 'install' in sys.argv:
    filename = resource_filename(Requirement.parse("update_pfsense_alias"), "etc/update_pfsense_alias/update_pfsense_alias.ini")
    os.mkdir("/etc/update_pfsense_alias")
    shutil.copy(filename, "/etc/update_pfsense_alias")
