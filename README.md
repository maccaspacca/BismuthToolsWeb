# BismuthTools Web Edition

Tools for the Bismuth Cryptocurrency

This repository contains tools for the Bismuth Cryptocurrency

For license see LICENSE file

See releases for pre-compiled versions (pre-compiled versions no longer available)

No promises are given that the tools will run on your particular system

Notes:

1. In order to take into account the use of Hyperblocks technology the query components are only designed to use blocks since the latest hyperblock in your ledger.
2. It is recommended that this tool be run against a full ledger

Requirements
============

Windows
=======

1. Bismuth cryptocurrency installed via the latest installation executable at https://github.com/hclivess/bismuth/releases or run from source
2. Full Bismuth node with full ledger mode
3. Python 3.5.3 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1896497
4. BS4 ([sudo] [pip] [pip3] install bs4)
5. Flask
6. tornado

Linux e.g. Ubuntu 16.04 LTS
===========================

1. Python 3.5.3 and dependencies as detailed at https://bitcointalk.org/index.php?topic=1896497
2. The Bismuth cryptocurrency installed from source (some additional python components such as pysocks may be needed depending on your installation)
3. Full Bismuth node with full ledger mode
4. BS4 ([sudo] [pip] [pip3] install bs4)
5. Flask
6. tornado

File placement
==============

The files can be placed on your desktop, in your home folder etc. depending on your OS, in a folder of your choosing.

The location of your ledger.db file must be set in the toolsconfig.ini file before running. Follow the comments in the file.

tools.db
=========

On first run, if there is no tools.db then a new one will be created.

This database is used to store sponsor, miner and richlist information and is updated every 30 minutes

Sponsors
========

Edit the toolsconfig.ini file as follows:

address = insert your the Bismuth address that will receive your payment

sponsors = insert 1 to switch on sponsors or 0 to switch off

rate = insert the number of blocks per Bismuth the sponsor advert will be displayed for

hostname = the base external hostname of the server e.g. bismuth.online

display = insert the maximum number of transaction records to be displayed on query of large addresses if set to zero this will return all transactions

front = insert the number of latest transactions to display on the front page

There are two sponsor spots on the main web landing page of the tools and a sponsor will be picked randomly from your sponsorlist.

Changes
=======
Version 4.2.0 29/12/2017
------------------------

1. Updates to information display
2. Currency display and conversion on richlist
3. No compiled releases in this version

Version 4.1.0 03/12/2017
------------------------

1. Updates to api
2. Minor fixes and adjustments
3. No compiled releases in this version

Version 4.0.1 25/10/2017
------------------------

1. Implement running flask on tornado web framework
2. Minor fixes and adjustments
3. No compiled releases in this version

Version 4.0.0 14/10/2017
------------------------

1. Move from Bottle to Flask
2. Initial API implementation
3. No compiled releases in this version

Version 3.0.1 12/09/2017
------------------------

1. Fix richlist display error
2. Fix text encode issue in bottle
3. No compiled releases in this version

Version 3.0.0 25/06/2017
------------------------

1. Python 3.5 support
2. Move from the web.py to the bottle web framework
3. Improve threading error fix from 2.0.3

Version 2.0.3 18/06/2017
------------------------

1. Ledgerquery threading error fix

Version 2.0.2 17/06/2017
------------------------

1. Tools database now updated using a copy of ledger.db placed in RAM
2. OG and other meta information now configured in toolsconfig.ini file
3. Minor fixes, typos and updates

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
4. Ledgerquery improvements allowing more efficient display for addresses with high numbers of transactions.

