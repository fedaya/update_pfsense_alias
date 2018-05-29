# update_pfsense_alias

update_pfsense_alias is a python script designed to resolve some IP addresses from domain name specified in a
configuration file and update an alias in pfsense using FauxAPI

## Installation

use the provided setup.py to install the project.
``update_pfsense_alias.ini`` is installed in ``/etc/update_pfsense_alias`` when recognising ``install`` command-line argument

## Usage
On the command-line, use:

```
update_pfsense_alias [ini_file]
```

## update_pfsense_alias.ini

An example ini file is provided and installed in ``/etc/update_pfsense_alias``
