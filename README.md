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
3. Python 3.5.3 or better and Bismuth node dependencies as detailed at https://bitcointalk.org/index.php?topic=1896497
4. BS4 ([sudo] [pip] [pip3] install bs4)
5. Flask
6. tornado
7. pyqrcode
8. requests

Linux e.g. Ubuntu 16.04 LTS
===========================

1. Python 3.5.3 or better and Bismuth node dependencies as detailed at https://bitcointalk.org/index.php?topic=1896497
2. The Bismuth cryptocurrency installed from source (some additional python components such as pysocks may be needed depending on your installation)
3. Full Bismuth node with full ledger mode
4. BS4 ([sudo] [pip] [pip3] install bs4)
5. Flask
6. tornado
7. pyqrcode
8. requests

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

Version 6.2.0 25/09/2018
------------------------

1. Front page display ordering fix
2. Reduction of code
3. Minor look and feel changes
4. Increase template use

Version 6.1.0 17/09/2018
------------------------

1. Bismuth URL creation tool
2. Realtime local mempool tool
3. Improved display of mirror blocks
4. Ledger queries of an address can be date limited
5. Minor code improvements
6. Sponsor handling improvements

Version 6.0.3 02/09/2018
------------------------

1. Issue 13 fix

Version 6.0.2 28/07/2018
------------------------

1. Issue 12 fix
2. Blocktime chart
3. Minor code changes

Version 6.0.1 26/07/2018
------------------------

1. Issue 11 fix - html content in openfield causing display problems

Version 6.0.0 18/07/2018
------------------------

Major update

1. Look and feel changes
2. Ledger query now includes alias query
3. Ledger query returns list with links to transaction details using simplified URL based on txid only
4. Removal of hash column on front page in favour of txid and link to transaction detail now included
5. Integration of operation field in query and details results
6. Update of API to include queries using alias, txid and returning results that include operation, txid, alias etc where appropriate
7. Minor code changes
8. Removal of old hyperlimit code
9. Query node directly for latest block and diff information

Future changes to include more charts and further reviews


Version 5.0.6 09/04/2018
------------------------

1. Issue 8 fix - Recommendation on wording - empty wallets

Version 5.0.5 08/03/2018
------------------------

1. Issue 7 fix - transactions not displayed for zero credit addresses e.g. mining pools
2. Version placed on title

Version 5.0.4 18/02/2018
------------------------

1. Issue 6 fix - transactions not displayed for zero balance addresses

Version 5.0.3 09/02/2018
------------------------

1. Cryptopia address query fix to allow display of all transactions

Version 5.0.2 02/02/2018
------------------------

1. Block hash query fix

Version 5.0.1 02/02/2018
------------------------

1. Query string trim

Version 5.0.0 01/02/2018
------------------------

Major version to aid transaction troubleshooting by exchanges

1. Replacement of Block Hash in ledger query with Transaction ID (this is based on first 56 characters of signature)
2. Transaction ID can be searched in ledger query
3. New feature to display transaction details bu clicking block number in ledger query results
4. Minor look and feel changes
5. No compiled releases in this version

Version 4.2.3 26/01/2018
------------------------

1. QF001012018 - fix CMC stats query. Now made every 5 minutes rather than on demand.
2. No compiled releases in this version

Version 4.2.2 18/01/2018
------------------------

1. Restrict richlist to those with BIS balance greater than bis_limit in toolsconfig.ini - default 1
2. Begin display of information charts - initially most recent difficulty (toolsconfig.ini > My Charts > diff =)
3. Charts on html template as precursor to future template use.
4. No compiled releases in this version

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

