README.md

# MOTIONBLINDS for FHEM

## An FHEMPY module to make use of motionblinds python library

By the way this is my first attempt to define a python module for FHEM

A firne dof mine has BREL motors that are controlable by Homeassistant and would like his fhem instance to pilot them as well. 

The motors are connected through a [BREL HUB](https://www.brel-home.nl/nl/pro/producten/smart-home/353/hub-03) (ethernet/RF) and a library alread exist in python (the one used by homeassistant)

[motion-blinds library](https://github.com/starkillerOG/motion-blinds)

In order to use python code in fhem the [fhempy](https://github.com/fhempy/fhempy/tree/master) module has to be installed:

Update the init.py of the library ...

            nano /opt/fhem/.fhempy/fhempy_venv/lib/python3.11/site-packages/motionblinds/__init__.py

Add the followig line at the end of the imports

            from .motion_blinds import MotionBlind

# Install fhempy

### Dependencies:

in a terminal, issue the following command:

    sudo apt install python3 python3-pip python3-dev python3-venv libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git libprotocol-websocket-perl
    
    sudo cpan Protocol::WebSocket

### Install and define fhempy

In fhem's command line do:

    update add https://raw.githubusercontent.com/fhempy/fhempy/master/controls_pythonbinding.txt

    update

    shutdown restart
    
    define fhempy_local BindingsIo fhempy

### Installation of motionblind library in fhem python environement

In orer to include the library do the following in a terminal, the first line defines the virtual python environement, the se'cond installs the library in it.

    source /opt/fhem/.fhempy/fhempy_venv/bin/activate
    
    pip install motionblinds

### install the fhempy module

To install the module, download motionblinds [master.zip](https://github.com/jcoenencom/motionblind) from github (the green <> CODE button on the top right, select Download ZIP) and unzip it
Rename the directory to motionblinds

 mv motionblind-master motionblinds

and copy the directory to fhempy libs and update the access rights

    sudo cp -r motionblinds /opt/fhem/.fhempy/fhempy_venv/lib/python3.11/site-packages/fhempy/lib/motionblinds
    sudo chown -R fhem /opt/fhem/.fhempy/fhempy_venv/lib/python3.11/site-packages/fhempy/lib/motionblinds
    sudo chgrp -R dialout /opt/fhem/.fhempy/fhempy_venv/lib/python3.11/site-packages/fhempy/lib/motionblinds

The module should normally come up.

## State of development:

Class motionblind is defined

A device can be created in fhem

    define brel fhempy motionblinds IP_address key

Where IP_address is the IP address of the motionblinds compatible hub, 
key is the key to grant access to the Hub functionalities.

![Device created on fhem](images/device.png)
