# BismuthTools Web Edition

Tools for the Bismuth Cryptocurrency

This repository contains tools for the Bismuth Cryptocurrency

For license see LICENSE file

See releases for pre-compiled versions

No promises are given that the tools will run on your particular system

Notes:

1. In order to take into account the use of Hyperblocks technology the query components are only designed to use blocks since the latest hyperblock in your ledger.

Requirements
============

Windows
=======

1. Windows 7 or better
2. Bismuth cryptocurrency installed via the latest installation executable at https://github.com/hclivess/bismuth/releases or run from source
3. The latest executable from releases https://github.com/maccaspacca/BismuthToolsWeb/releases use "bismuthtoolsweb.exe" and access from a browser (localhost:8080)

Run from source
1. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
2. wxpython for your Python 2.7 installation as found here: https://wxpython.org/download.php
3. If you have sponsors enabled then you will need BS4 (pip install bs4)
4. If you wish you can compile your own executables using pyinstaller and the .cmd files provided

Linux e.g. Ubuntu 16.04 LTS
===========================

1. Python 2.7 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1525078
2. The Bismuth cryptocurrency installed from source (some additional python components such as pysocks may be needed depending on your installation)
4. If you have sponsors enabled then you will need BS4 (pip install bs4)
5. You can also compile your own executables using pyinstaller and the .cmd file provided or use the ones provided in releases

File placement
==============

The files can be placed on your desktop, in your home folder etc. depending on your OS, in a folder of your choosing.

The location of your ledger.db file must be set in the toolsconfig.ini file before running. Follow the comments in the file.

The windows installer executable will create the tools folder for you on at "c:\toolsweb"

tools.db
=========

On first run, if there is no tools.db then a new one will be created.

This database is used to store sponsor, miner and richlist information and is updated every 30 minutes

Sponsors
========

Edit the toolsconfig.ini file as follows:

address = <insert your the Bismuth address that will receive your payment>

sponsors = <insert 1 to switch on sponsors or 0 to switch off>

rate = <insert the number of blocks per Bismuth the sponsor advert will be displayed for>

There are two sponsor spots on the main web landing page of the tools and a sponsor will be picked randomly from your sponsorlist.

Changes
=======

Version 2.0.1 21/05/2017
------------------------

1. Path to database location configured in new toolsconfig.ini file
2. Sponsor information moved to new toolsconfig.ini file
3. Fix compatibility with hyperblock enabled ledger.db
4. Fix sponsor url parsing error
5. Confirm pull request to use GMT time for display of timestamps
6. Remove old code and tidy up

Version 2.0.0 14/05/2017
------------------------

1. Split from desktop tools into its own repository
2. Implementation of richlist
3. Combined database for miners, sponsors and richlist
4. Allow alternative placement out of the main Bismuth folder by OS detect and assumed ledger.db location
5. Remove inaccurate miner information e.g. power usage as this is not relevant to production

Future Improvements:

1. Other Ledger Information page: to list hyperblock and query "keep" transactions
2. Network information page
3. Look and feel improvements
4. Pyhton 3.x compatibility
5. Move sponsors from local definition to blockchain with payments shared between those hosting webtools

