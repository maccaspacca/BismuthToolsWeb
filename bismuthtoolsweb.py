# Bismuth Tools Web Edition
# Version 5.0.4
# Date 18/02/2018
# Copyright Maccaspacca 2017, 2018
# Copyright Hclivess 2016 to 2018
# Author Maccaspacca

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from flask import Flask, request
from flask import Markup
from flask import render_template
app = Flask(__name__)

import json, sqlite3, time, re, os
import threading
from bs4 import BeautifulSoup
import logging, random, platform, requests
import configparser as cp
from urllib.request import urlopen
	
# globals
global my_os
global bis_root
global myaddress
global myrate
global mysponsor
global disp_curr

disp_curr = ["BTC","USD","EUR","GBP","CNY","AUD"]

logging.basicConfig(level=logging.INFO, 
                    filename='toolsdb.log', # log to this file
                    format='%(asctime)s %(message)s') # include timestamp

logging.info("logging initiated")

config = cp.ConfigParser()
config.readfp(open(r'toolsconfig.ini'))
logging.info("Reading config file.....")
mysponsor = int(config.get('My Sponsors', 'sponsors'))
myaddress = config.get('My Sponsors', 'address')
myrate = float(config.get('My Sponsors', 'rate'))
myhost = config.get('My Sponsors', 'hostname')
try:
	mydisplay = int(config.get('My Sponsors', 'display'))
except:
	mydisplay = 0
bis_root = config.get('My Bismuth', 'dbpath')
try:
	front_display = config.get('My Sponsors', 'front')
except:
	front_display = 15
try:
	cust_curr = config.get('My Sponsors', 'currency')
except:
	cust_curr = "EUR"
try:
	bis_limit = int(config.get('My Bismuth', 'bis_limit'))
except:
	bis_limit = 1
try:
	topia = config.get('My Bismuth', 'cryptopia')
except:
	topia = "edf2d63cdf0b6275ead22c9e6d66aa8ea31dc0ccb367fad2e7c08a25" # cryptopia address
try:
	diff_ch = int(config.get('My Charts', 'diff'))
except:
	diff_ch = 50

logging.info("Config file read completed")
config = None

if mysponsor == 1:
	mysponsor = True
else:
	mysponsor = False

my_os = platform.system()
my_os = my_os.lower()

if "linux" in my_os:
	bis_root = os.path.expanduser('{}'.format(bis_root))
elif "windows" in my_os:
	pass
else: # if its not windows then probably a linux or unix variant
	pass

print("Bismuth path = {}".format(bis_root))


def get_cmc_info(alt_curr):

	ch = "price_{}".format(alt_curr.lower())

	try:
		t = "https://api.coinmarketcap.com/v1/ticker/bismuth/?convert={}".format(alt_curr)
		r = requests.get(t)
		x = r.text
		y = json.loads(x)
		c_btc = y[0]['price_btc']
		c_usd = "{:.2f}".format(float(y[0]['price_usd']))
		c_cus = "{:.2f}".format(float(y[0][ch]))
		# print( y )
		s = "<p><b> LATEST PRICES: BTC = {} | USD = {} | {} = {}</b></p>".format(c_btc,str(c_usd),alt_curr,str(c_cus))
		
	except requests.exceptions.RequestException as e:
		s = "Error: {}".format(e)

	return s
	
def get_cmc_val(alt_curr):

	ch = "price_{}".format(alt_curr.lower())

	try:
		t = "https://api.coinmarketcap.com/v1/ticker/bismuth/?convert={}".format(alt_curr)
		r = requests.get(t)
		x = r.text
		y = json.loads(x)
		s = float(y[0][ch])
		
	except:
		s = 0.00000001

	return s
	
def myoginfo():

	doda = []
	doconfig = cp.ConfigParser()
	doconfig.readfp(open(r'toolsconfig.ini'))
	logging.info("Reading config file.....")
	doda.append(doconfig.get('My Oginfo', 'og_title'))
	doda.append(doconfig.get('My Oginfo', 'og_description'))
	doda.append(doconfig.get('My Oginfo', 'og_url'))
	doda.append(doconfig.get('My Oginfo', 'og_site_name'))
	doda.append(doconfig.get('My Oginfo', 'og_image'))

	logging.info("Config file read completed")
	
	doconfig = None
	
	return doda
	
def latest():

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE reward != 0 ORDER BY block_height DESC LIMIT 1;") #or it takes the first
	result = c.fetchall()

	db_timestamp_last = result[0][1]
	db_block_height = result[0][0]
	db_block_finder = result[0][2]
	db_block_hash = result[0][7]
	db_block_open = result[0][11]
	time_now = str(time.time())
	last_block_ago = float(time_now) - float(db_timestamp_last)
	
	global hyper_limit
	
	c.execute("SELECT * FROM transactions WHERE address = ? OR address = ? ORDER BY block_height DESC LIMIT 1;", ('Hypoblock','Hyperblock')) #or it takes the first
	hyper_result = c.fetchall()
	
	c.execute("SELECT difficulty FROM misc ORDER BY block_height DESC LIMIT 1")
	diff_block_previous = float(c.fetchone()[0])
	
	c.close()
	conn.close()
	
	if not hyper_result:
		hyper_limit = 1
	else:
		hyper_limit = (hyper_result[0][0]) + 1
	
	logging.info("Latest block queried: {}".format(str(db_block_height)))
	logging.info("Hyper_Limit is: {}".format(str(hyper_limit)))

	return db_block_height, last_block_ago, diff_block_previous, db_block_finder, db_timestamp_last, db_block_hash, db_block_open

def getmeta(this_url):
# This module attempts to get Open Graph information for the sponsor site_name
# If this fails it attempts to use the "name" property before just filling the info with the url

	this_property = ("og:title","og:image","og:url","og:description","og:site_name")
	oginfo = []

	url = urlopen(this_url)

	webpage = url.read()

	soup = BeautifulSoup(webpage, "html.parser")
	
	for prop in this_property:
		temp_tag = soup.find("meta", {"property": prop})
		if temp_tag is not None:
			oginfo.append(str(temp_tag["content"]))
		else:
			ex_prop = prop.split(":")[1]
			ex_tag = soup.find("meta", {"name": ex_prop})
			if ex_tag is not None:
				oginfo.append(str(ex_tag["content"]))
			else:
				oginfo.append("")

	return oginfo

def i_am_first(my_first,the_address):

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT MIN(block_height) FROM transactions WHERE openfield = ?;",(my_first,))
	test_min = c.fetchone()[0]
	c.execute("SELECT * FROM transactions WHERE block_height = ? and openfield = ?;",(test_min,my_first))
	test_me = c.fetchone()[2]
	c.close()
	
	#print(str(the_address) + " | " + str(test_me))
	
	if the_address == test_me:
		return True
	else:
		return False

# check miner address for a nickname

def checkmyname(myaddress):

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE address = ? AND recipient = ? AND amount > ? AND openfield LIKE 'Minername=%' ORDER BY block_height ASC;",(myaddress,myaddress,"1"))
	namelist = c.fetchall()
	c.close()
	
	goodname = ""

	for x in namelist:
		tempfield = str(x[11])
		
		if i_am_first(tempfield,x[2]):
			duff = tempfield.split("=")
			goodname = str(duff[1])
		else:
			goodname = ""

	logging.info("Tools DB: Check miner name result: Address {} = {}".format(str(myaddress),goodname))
		
	return goodname
	
def checkalias(myaddress):

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE address = ? AND recipient = ? AND fee != 0  AND openfield LIKE 'alias=%' ORDER BY block_height ASC;",(myaddress,myaddress))
	namelist = c.fetchall()
	c.close()
	
	goodname = ""

	for x in namelist:
		tempfield = str(x[11])
		if "alias=" in tempfield:
				if i_am_first(tempfield,x[2]):
					duff = tempfield.split("=")
					goodname = str(duff[1])
				else:
					goodname = ""
					
	if myaddress == "4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed":
		goodname = "Test and Development Fund"
	if myaddress == "edf2d63cdf0b6275ead22c9e6d66aa8ea31dc0ccb367fad2e7c08a25":
		goodname = "Cryptopia Exchange"
	if myaddress == "01d616b9df2a85a3e9df92d421a49217bad7a5a5ffc34cf1a095cb5a":
		goodname = "Acc-Pool Mining"

	#logging.info("Tools DB: Check alias result: Address {} = {}".format(str(myaddress),goodname))

	return goodname
	
# get and process address information	

def refresh(testAddress,typical):

	if typical == 1:
		conn = sqlite3.connect(bis_root)
		conn.text_factory = str
		c = conn.cursor()
	elif typical == 2:
		conn = sqlite3.connect(bis_root)
		conn.text_factory = str
		c = conn.cursor()
	else:
		pass
	
	c.execute("SELECT sum(amount) FROM transactions WHERE recipient = ?;",(testAddress,))
	credit = c.fetchone()[0]
	c.execute("SELECT sum(amount),sum(fee),sum(reward) FROM transactions WHERE address = ?;",(testAddress,))
	tester = c.fetchall()

	debit = tester[0][0]
	fees = tester[0][1]
	rewards = tester[0][2]
	
	if not rewards:
		rewards = 0
	
	if rewards > 0:		
		c.execute("SELECT count(*) FROM transactions WHERE address = ? AND (reward != 0);",(testAddress,))
		b_count = c.fetchone()[0]
		c.execute("SELECT MAX(timestamp) FROM transactions WHERE recipient = ? AND (reward !=0);",(testAddress,))
		t_max = c.fetchone()[0]
		c.execute("SELECT MIN(timestamp) FROM transactions WHERE recipient = ? AND (reward !=0);",(testAddress,))
		t_min = c.fetchone()[0]

		t_min = str(time.strftime("at %H:%M:%S on %d/%m/%Y", time.gmtime(float(t_min))))
		t_max = str(time.strftime("at %H:%M:%S on %d/%m/%Y", time.gmtime(float(t_max))))
	else:
		b_count = 0
		t_min = 0
		t_max = 0
	
	if not debit:
		debit = 0
	if not fees:
		fees = 0
	if not rewards:
		rewards = 0
	if not credit:
		credit = 0

	balance = (credit + rewards) - (debit + fees)

	c.close()
	
	if typical == 1:
		conn.close()
	
	get_stuff = [str(credit),str(debit),str(rewards),str(fees),str(balance),t_max, t_min, b_count]
		
	return get_stuff
	
def sponsor_list(thisaddress,thisrate):

	mysponsors = []

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE recipient = ? AND instr(openfield, 'sponsor=') > 0;",(thisaddress,))
	mysponsors = c.fetchall()
	c.close()

	the_sponsors = []

	for dudes in mysponsors:

		dud = dudes[11].split("sponsor=")

		try:
			temp_block = dudes[0]
			temp_paid = float(dudes[4])
			max_block = temp_block + (int(round(temp_paid * thisrate)) + 100)

			latest_block = latest()
						
			if latest_block[0] < max_block:
				temp_ogs = getmeta(str(dud[1]))
				the_sponsors.append((temp_ogs[0],temp_ogs[1],temp_ogs[2],temp_ogs[3],str(max_block),str(temp_block),temp_ogs[4]))
			else:
				pass
			
		except:
			pass

	if not the_sponsors:
		the_sponsors.append(("Bismuth","https://i1.wp.com/bismuth.cz/wp-content/uploads/2017/03/cropped-mesh2-2.png","http://bismuth.cz/","In the truly free world, there are no limits","500000","68924","Bismuth"))
			
	return the_sponsors
	
def updatedb():

	print("Updating database.....wait")
	
	logging.info("Tools DB: Rebuild")

	# create empty tools database
	tools = sqlite3.connect('temptools.db')
	tools.isolation_level = None
	tools.text_factory = str
	m = tools.cursor()
	m.execute("CREATE TABLE IF NOT EXISTS richlist (address, balance, alias)")
	m.execute("CREATE TABLE IF NOT EXISTS minerlist (address, blatest, bfirst, blockcount, treward, mname)")
	m.execute("CREATE TABLE IF NOT EXISTS sponsorlist (title, image, url, description, end, paid, name)")
	tools.commit()

	logging.info("Tools DB: Creating or updating tools database")
		
	logging.info("Tools DB: Getting info.....")

# sponsors ///////////////////////////////////////////////////

	logging.info("Tools DB: Getting up to date list of sponsors.....")

	the_sponsors = sponsor_list(myaddress,myrate)
			
	logging.info("Tools DB: Inserting sponsor information into database.....")
			
	for y in the_sponsors:

		m.execute('INSERT INTO sponsorlist VALUES (?,?,?,?,?,?,?)', (y[0],y[1],y[2],y[3],y[4],y[5],y[6]))
	tools.commit()

# ////////////////////////////////////////////////////////////

# rich and miner lists ///////////////////////////////////////

	r_all = []
	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	r = conn.cursor()
	r.execute("SELECT distinct recipient FROM transactions WHERE amount !=0 OR reward !=0;")
	r_all = r.fetchall()
	r.close()
	
	logging.info("Tools DB: getting richlist and minerlist information.....")
	
	m.execute("begin")

	for x in r_all:

		btemp = refresh(str(x[0]),2)
		m_alias = checkalias(str(x[0]))
		print(str(x[0]))
		#print(m_alias)
		amirich = float(btemp[4])
		if amirich > bis_limit:
			#print(str(amirich))
			m.execute('INSERT INTO richlist VALUES (?,?,?)', (x[0],btemp[4],m_alias))

		if float(btemp[2]) > 0:
			temp_miner = str(x[0])
			if len(temp_miner) == 56:
				m_name = checkmyname(temp_miner)
				if len(m_name) == 0:
					if len(m_alias) > 0:
						m_name = m_alias
				m.execute('INSERT INTO minerlist VALUES (?,?,?,?,?,?)', (temp_miner, btemp[5], btemp[6], btemp[7], btemp[2], m_name))
		
	m.execute("commit")
	tools.commit()
	m.close()
	tools.close()
	
	time.sleep(5)

	if os.path.isfile('tools.db'):
		os.remove('tools.db')
	os.rename('temptools.db','tools.db')
	logging.info("Tools DB: Done !")
	
	return True

def buildtoolsdb():

	global home_stats
	global cmc_vals
	cmc_vals = []
	home_stats = get_cmc_info(cust_curr)
	cmc_vals.append(get_cmc_val("BTC"))
	time.sleep(1)
	cmc_vals.append(get_cmc_val("USD"))
	time.sleep(1)
	cmc_vals.append(get_cmc_val("EUR"))
	time.sleep(1)
	cmc_vals.append(get_cmc_val("GBP"))
	time.sleep(1)
	cmc_vals.append(get_cmc_val("CNY"))
	time.sleep(1)
	cmc_vals.append(get_cmc_val("AUD"))
	
	updatedb()
	
	i = 0
	
	while True:
	
		print("Stats: Waiting for 5 minutes.......")
		time.sleep(300)
		cmc_vals = []
		home_stats = get_cmc_info(cust_curr)
		cmc_vals.append(get_cmc_val("BTC"))
		time.sleep(1)
		cmc_vals.append(get_cmc_val("USD"))
		time.sleep(1)
		cmc_vals.append(get_cmc_val("EUR"))
		time.sleep(1)
		cmc_vals.append(get_cmc_val("GBP"))
		time.sleep(1)
		cmc_vals.append(get_cmc_val("CNY"))
		time.sleep(1)
		cmc_vals.append(get_cmc_val("AUD"))
		i +=1
		if i == 6:
			bobble = updatedb()
			print("Tools DB: Waiting for 30 minutes.......")
			i = 0

def checkstart():

	if not os.path.exists('tools.db'):
		# create empty miners database
		logging.info("Tools DB: Create New as none exists")
		mlist = sqlite3.connect('tools.db')
		mlist.text_factory = str
		m = mlist.cursor()
		m.execute("CREATE TABLE IF NOT EXISTS richlist (address, balance, alias)")
		m.execute("CREATE TABLE IF NOT EXISTS minerlist (address, blatest, bfirst, blockcount, treward, mname)")
		m.execute("CREATE TABLE IF NOT EXISTS sponsorlist (title, image, url, description, end, paid, name)")
		mlist.commit()
		mlist.close()
		# create empty tools.db

latest()
checkstart()

# get coins in circulation

def getcirc():

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT sum(reward) FROM transactions;")

	allcirc = c.fetchone()[0]
	
	c.execute("SELECT sum(amount) FROM transactions WHERE address = 'Development Reward';")
	
	alldev = c.fetchone()[0]

	c.execute("SELECT sum(amount) FROM transactions WHERE address = 'Hyperblock';")
	
	allhyp = c.fetchone()[0]
	
	if not allhyp:
		allhyp = 0
	if not alldev:
		alldev = 0

	allcirc = float(allcirc) + float(alldev) + float(allhyp)

	c.close()
	conn.close()	
	
	return allcirc

# get latest 15 transactions

def getall():

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions ORDER BY block_height DESC, timestamp DESC LIMIT ?;", (front_display,))

	myall = c.fetchall()
	
	c.close()
	conn.close()
	
	return myall
	
def get_open(thisblock,thisopen):

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE block_height = ? AND openfield = ?;", (thisblock,thisopen))

	myopen = c.fetchone()
	c.close()
	conn.close()
	
	return myopen
	

def test(testString):

	if len(testString) == 56:
		if (re.search('[abcdef]',testString)):
			test_result = 1
		else:
			test_result = 3

	elif testString.isdigit() == True:
		test_result = 2
	else:
		test_result = 3
	
	#print(test_result)
	return test_result
	
def s_test(testString):

	if testString.isalnum():
		if (re.search('[abcdef]',testString)):
			if len(testString) == 56:
				return True
	else:
		return False

def miners():

	logging.info("Tools DB: Get mining addresses from tools.db")
	conn = sqlite3.connect('tools.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM minerlist ORDER BY blockcount DESC;")
	miner_result = c.fetchall()
	c.close()
	conn.close()

	return miner_result

def richones():

	logging.info("Tools DB: Get rich addresses from tools.db")
	conn = sqlite3.connect('tools.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM richlist ORDER BY balance DESC;")
	rich_result = c.fetchall()
	c.close()
	conn.close()

	return rich_result
	
def get_alias(address):

	try:
		conn = sqlite3.connect('tools.db')
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT alias FROM richlist WHERE address=?;", (address,))
		r_alias = c.fetchone()[0]
		c.close()
		conn.close()
		
		if not r_alias:
			r_alias = ""
	except:
		r_alias = ""
		
	return str(r_alias)
	
def get_sponsor():

	if mysponsor:
	
		logging.info("Sponsors: Get sites from tools.db")
		conn = sqlite3.connect('tools.db')
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT * FROM sponsorlist;")
		sponsor_result = c.fetchall()
		c.close()
		conn.close()
		
		x_top = len(sponsor_result) -1
		x_go = random.randint(0,x_top)
		
		sponsor_display = []
		
		sponsor_display.append('<table style="width: 200px;">\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;"><a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('{}</a></td>\n'.format(sponsor_result[x_go][6]))
		sponsor_display.append('</tr>\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;">\n')
		sponsor_display.append('<a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('<img src="{}" alt="{}" height="100px">'.format(sponsor_result[x_go][1],sponsor_result[x_go][3]))
		sponsor_display.append('</img></a>\n')
		sponsor_display.append('</td>\n')
		sponsor_display.append('</tr>\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;"><a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('{}</a></td>\n'.format(sponsor_result[x_go][0]))
		sponsor_display.append('</tr>\n')
		sponsor_display.append('</table>\n')
		
		logging.info("Sponsors: {} was displayed".format(sponsor_result[x_go][2]))
	
	else:
		sponsor_display = []
		sponsor_display.append('<p></p>')

	return sponsor_display

def bgetvars(myaddress):

	try:
		conn = sqlite3.connect('tools.db')
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT * FROM minerlist WHERE address = ?;",(myaddress,))
		miner_details = c.fetchone()
		c.close()
		conn.close()
	except:
		miner_details = None
		
	return miner_details
	

def my_head(bo):

	mhead = []
	dado = myoginfo()
	
	mhead.append('<!doctype html>\n')
	mhead.append('<html>\n')
	mhead.append('<head>\n')
	mhead.append('<link rel = "icon" href = "static/explorer.ico" type = "image/x-icon" />\n')
	mhead.append('<style>\n')
	mhead.append('h1, h2, p, li, td, label {font-family: Verdana;}\n')
	mhead.append('body {font-size: 75%;}\n')
	mhead.append('ul {list-style-type: none;margin: 0;padding: 0;overflow: hidden;background-color: #333;}\n')
	mhead.append('li {float: left;}\n')
	mhead.append('li a {display: inline-block;color: white;text-align: center;padding: 14px 16px;text-decoration: none;}\n')
	mhead.append('li a:hover {background-color: #111;}\n')
	mhead.append('.btn-link{border:none;outline:none;background:none;cursor:pointer;color:#0000EE;padding:0;text-decoration:underline;font-family:inherit;font-size:inherit;}\n')
	mhead.append(bo + '\n')
	mhead.append('</style>\n')
	mhead.append('<meta property="og:type" content="website" />\n')
	mhead.append('<meta property="og:title" content="{}" />\n'.format(dado[0]))
	mhead.append('<meta property="og:description" content="{}" />\n'.format(dado[1]))
	mhead.append('<meta property="og:url" content="{}" />\n'.format(dado[2]))
	mhead.append('<meta property="og:site_name" content="{}" />\n'.format(dado[3]))
	mhead.append('<meta property="og:image" content="{}" />\n'.format(dado[4]))
	mhead.append('<meta property="og:image:width" content="200" />\n')
	mhead.append('<meta property="og:image:height" content="200" />\n')
	mhead.append('<meta property="og:locale" content="en_US" />\n')
	mhead.append('<meta property="xbm:version" content="201" />\n')
	mhead.append('<meta name="description" content="{}" />\n'.format(dado[1]))
	mhead.append('<title>{}</title>\n'.format(dado[0]))
	mhead.append('</head>\n')
	mhead.append('<body background="static/explorer_bg.png">\n')
	mhead.append('<center>\n')
	mhead.append('<table style="border:0">\n')
	mhead.append('<tr style="border:0"><td style="border:0">\n')
	mhead.append('<ul>\n')
	mhead.append('<li><a href="">Menu:</a></li>\n')
	mhead.append('<li><a href="/">Home</a></li>\n')
	mhead.append('<li><a href="/ledgerquery">Ledger Query</a></li>\n')
	mhead.append('<li><a href="/minerquery">Miner Stats</a></li>\n')
	mhead.append('<li><a href="/richest">Rich List</a></li>\n')
	if mysponsor:
		mhead.append('<li><a href="/sponsorinfo">Sponsors</a></li>\n')
	mhead.append('<li><a href="/apihelp">API</a></li>\n')
	mhead.append('<li><a href="/charts">Charts</a></li>\n')
	mhead.append('</ul>\n')
	mhead.append('</td></tr>\n')
	mhead.append('</table>\n')

	return mhead
	
#////////////////////////////////////////////////////////////
#                       MAIN APP
# ///////////////////////////////////////////////////////////

#@app.route('/static/<filename>')
#def server_static(filename):
	#return static_file(filename, root='static/')

@app.route('/')
def home():

	currcoins = getcirc()
	thisall = getall()
	
	thisview = []

	i = 0

	for x in thisall:
		if i % 2 == 0:
			color_cell = "#E8E8E8"
		else:
			color_cell = "white"

		a_from = get_alias(str(x[2]))
		if a_from == "":
			a_from = str(x[2])
		else:
			a_from = "<b>{}</b>\n{}".format(a_from,str(x[2]))
		if str(x[2]) == str(x[3]):
			a_to = a_from
		else:
			a_to = get_alias(str(x[3]))
			if a_to == "":
				a_to = str(x[3])
			else:
				a_to = "<b>{}</b>\n{}".format(a_to,str(x[3]))
						
		thisview.append('<tr bgcolor ="{}">'.format(color_cell))
		thisview.append('<td>{}</td>'.format(str(x[0])))
		thisview.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))))))
		thisview.append('<td>{}</td>'.format(a_from)) # from
		thisview.append('<td>{}</td>'.format(a_to)) # to
		thisview.append('<td>{}</td>'.format(str(x[4])))
		thisview.append('<td>{}</td>'.format(str(x[7])))
		thisview.append('<td>{}</td>'.format(str(x[8])))
		thisview.append('<td>{}</td>'.format(str(x[9])))
		thisview.append('</tr>\n')
		i = i+1		

	#initial = my_head('table, th, td {border: 0;}')
	initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')

	initial.append('<table ><tbody><tr>\n')
	initial.append('<td align="center" style="border:hidden;">')
	sponsor1 = get_sponsor()
	initial = initial + sponsor1
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">\n')
	initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
	initial.append('<h2>Welcome to the Bismuth Tools Web Edition</h2>\n')
	initial.append('<p>Choose what you want to do next by clicking an option from the menu above</p>\n')
	initial.append('<p><b>There are {} Bismuth in circulation</b></p>\n'.format(str(currcoins)))
	initial.append('<h2>Last {} Transactions</h2>\n'.format(front_display))
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">')
	sponsor2 = get_sponsor()
	initial = initial + sponsor2
	initial.append('</td>\n')
	initial.append('</tr><tr>\n')
	initial.append('<td colspan="3" align="center" style="border:hidden;">\n')
	#cmcstats = get_cmc_info(cust_curr)
	cmcstats = home_stats
	initial.append('{}'.format(cmcstats))
	initial.append('</td>\n')
	initial.append('</tr></tbody></table>\n')
	initial.append('<table style="font-size: 76%">\n')
	initial.append('<tr>\n')
	initial.append('<td><b>Block</b></td>\n')
	initial.append('<td><b>Timestamp</b></td>\n')
	initial.append('<td><b>From</b></td>\n')
	initial.append('<td><b>To</b></td>\n')
	initial.append('<td><b>Amount</b></td>\n')
	initial.append('<td><b>Block Hash</b></td>\n')
	initial.append('<td><b>Fee</b></td>\n')
	initial.append('<td><b>Reward</b></td>\n')
	initial.append('</tr>\n')
	initial = initial + thisview
	initial.append('</table>\n')
	initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	initial.append('<p>Price information courtesy of coinmarketcap.com</p>')
	initial.append('</center>\n')
	initial.append('</body>\n')
	initial.append('</html>')

	starter = "" + str(''.join(initial))

	return starter.encode("utf-8")
	
@app.route('/diff_chart')
def chart():

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM misc ORDER BY block_height DESC LIMIT ?;", (diff_ch,))
	d_result = c.fetchall()
	b = []
	d = []
	d_result = list(reversed(d_result))
	for v in d_result:
		b.append(v[0])
		d.append(float(v[1]))
	
	c.close()
	conn.close()	
	
	legend = 'Difficulty'

	return render_template('chart.html', values=d, labels=b, legend=legend)
	

@app.route('/minerquery', methods=['GET'])
def minerquery():

	try:
		getaddress = request.args.get('myaddy') or ""
	except:
		getaddress = None

	#Nonetype handling - simply replace with ""

	if not getaddress:
		addressis = ""
	elif getaddress == "":
		addressis = ""
	else:
		#print("Info requested: " + getaddress)
		m_info = bgetvars(getaddress)
		addressis = "<table style='width:50%;'>"
		addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Address:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[0]))
		addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Latest Block Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[1]))
		addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>First Block Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[2]))
		addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Blocks Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[3]))
		addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Rewards:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[4]))
		addressis = addressis + "</table>"

	all = miners()
	
	view = []
	i = 0
	j = 1
	for x in all:
		thisminer = str(x[0])
		if len(thisminer) == 56:
			if j % 2 == 0:
				color_cell = "white"
			else:
				color_cell = "#E8E8E8"
			view.append("<tr bgcolor ='{}'>".format(color_cell))
			view.append("<td>{}</td>".format(str(j)))
			if len(str(x[5])) > 0:
				view.append("<td><a href='/minerquery?myaddy={}'>{}</a></td>".format(thisminer,str(x[5])))
			else:
				view.append("<td><a href='/minerquery?myaddy={}'>{}</a></td>".format(thisminer,thisminer))					
			view.append("<td>{}</td>".format(str(x[3])))				
			j = j+1
		view.append("</tr>\n")
		i = i+1
	
	lister = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
	lister.append('<h2>Bismuth Miner Statistics</h2>\n')
	if hyper_limit > 1:
		lister.append('<p><b>Mining statistics since block number: {}</b></p>\n'.format(str(hyper_limit)))
	lister.append('<p><b>Hint: Click on an address to see more detail</b></p>\n')
	lister.append('<p>Note: this page may be up to 45 mins behind</p>\n')
	lister.append('<p style="color:#08750A">{}</p>\n'.format(addressis))
	lister.append('<p></p>\n')
	lister.append('<table style="width:60%" bgcolor="white">\n')
	lister.append('<tr>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Rank</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Miner</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Blocks Found</b></td>\n')
	lister.append('</tr>\n')
	lister = lister + view
	lister.append('</table>\n')
	lister.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	lister.append('</center>\n')
	lister.append('</body>\n')
	lister.append('</html>')

	html = "" + str(''.join(lister))

	return html.encode("utf-8")

@app.route('/ledgerquery', methods=['GET'])
def ledger_form():
		
	mylatest = latest()
	
	plotter = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
	plotter.append('<h2>Bismuth Ledger Query Tool</h2>\n')
	plotter.append('<p>Get a List of Transactions</p>\n')
	plotter.append('<form method="post" action="/ledgerquery">\n')
	plotter.append('<table>\n')
	plotter.append('<tr><th><label for="block">Enter a Block Number, txid, Hash or Address</label></th><td><input type="text" id="block" name="block" size="58"/></td></tr>\n')
	plotter.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
	plotter.append('</table>\n')
	plotter.append('</form>\n')
	#plotter.append('</p>\n')
	plotter.append('<p>The latest block: {} was found {} seconds ago at difficulty {}</p>\n'.format(str(mylatest[0]),str(int(mylatest[1])),str(mylatest[2])))
	if hyper_limit > 1:
		plotter.append('<p>The last Hyperblock was at block: {}</p>\n'.format(str(hyper_limit)))
		plotter.append('<p>Queries for blocks before {} will not be found</p>\n'.format(str(hyper_limit)))
	plotter.append('</body>\n')
	plotter.append('</html>')
	# Initial Form

	html = "" + str(''.join(plotter))

	return html.encode("utf-8")

@app.route('/ledgerquery', methods=['POST'])
def ledger_query():
	
	mylatest = latest()

	myblock = request.form.get('block')
	
	#Nonetype handling - simply replace with "0"
	
	if not myblock:
		myblock = "0"
	
	#if not myblock.isalnum():
		#myblock = "0"
		#print("has dodgy characters but now fixed")
	
	myblock = myblock.strip()
	
	my_type = test(myblock)
	
	if my_type == 3:
		myblock = "0"
		my_type = 2
	
	if my_type == 1:
		
		myxtions = refresh(myblock,1)
		
		if float(myxtions[0]) > 0:
		
			extext = "<p style='color:#08750A'><b>ADDRESS FOUND | Credits: {} | Debits: {} | Rewards: {} |".format(myxtions[0],myxtions[1],myxtions[2])
			extext = extext + " Fees: {} | BALANCE: {}</b></p>".format(myxtions[3],myxtions[4])
			
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC;", (str(myblock),str(myblock)))
			
			temp_all = c.fetchall()

			if mydisplay == 0:
				all = temp_all
			elif str(myblock) == topia:
				all = temp_all
			else:
				all = temp_all[:mydisplay]
			
			c.close()
			conn.close()
		
		else:

			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_hash = ?;", (str(myblock),))

			all = c.fetchall()
			
			c.close()
			conn.close()
		
			if not all:
			
				conn = sqlite3.connect(bis_root)
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE instr(signature, ?) > 0;",(str(myblock),))

				all = c.fetchall()
				
				c.close()
				conn.close()
				
			if not all:				
				extext = "<p style='color:#C70039'>Error !!! Nothing found for the address, txid or hash you entered</p>"
			else:
				extext = "<p>Transaction found for ID given</p>"
	
	if my_type == 2:
	
		if myblock == "0":
		
			all = []
		
		else:
		
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_height = ?;", (myblock,))

			all = c.fetchall()
			#print(all)
			
			c.close()
			conn.close()
	
		if not all:
			extext = "<p style='color:#C70039'>Error !!! Block, address or hash not found. Maybe you entered bad data or nothing at all?</p>\n"
		else:
			pblock = int(myblock) -1
			nblock = int(myblock) +1
			extext = "<form action='/ledgerquery' method='post'><table><tr>\n"
			if pblock > (hyper_limit - 2):
				extext = extext + "<td style='border:hidden;'><button type='submit' name='block' value='{}' class='btn-link'><< Previous Block</button></td>\n".format(str(pblock))
			else:
				extext = extext + "<td style='border:hidden;'><p></p></td>\n"			
			extext = extext + "<td style='border:hidden;'><p><b>Transactions for block {}</b></p></td>\n".format(str(myblock))
			if nblock < (int(mylatest[0]) + 1):
				extext = extext + "<td style='border:hidden;'><button type='submit' name='block' value='{}' class='btn-link'>Next Block >></button></td>\n".format(str(nblock))
			else:
				extext = extext + "<td style='border:hidden;'><p></p></td>\n"
			extext = extext + "</tr></table></form>\n"
	
	view = []
	i = 0
	for x in all:
		if i % 2 == 0:
			color_cell = "#E8E8E8"
		else:
			color_cell = "white"
		det_link = "/details?mydetail={}:{}:{}:{}".format(str(x[0]),str(x[2]),str(x[3]),str(x[4]))
		view.append('<tr bgcolor ="{}">'.format(color_cell))
		view.append('<td><a href="{}">{}</a></td>'.format(det_link,str(x[0])))
		view.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))))))
		view.append('<td>{}</td>'.format(str(x[2])))
		view.append('<td>{}</td>'.format(str(x[3])))
		view.append('<td>{}</td>'.format(str(x[4])))
		view.append('<td>{}</td>'.format(str(x[5][:56])))
		view.append('<td>{}</td>'.format(str(x[8])))
		view.append('<td>{}</td>'.format(str(x[9])))
		view.append('<td>{}</td>'.format(str(x[11][:20])))
		view.append('</tr>\n')
		i = i+1
	
	replot = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
	replot.append('<h2>Bismuth Ledger Query Tool</h2>\n')
	replot.append('<p>Get a List of Transactions</p>\n')
	replot.append('<form method="post" action="/ledgerquery">\n')
	replot.append('<table>\n')
	replot.append('<tr><th><label for="block">Enter a Block Number, txid, Hash or Address</label></th><td><input type="text" id="block" name="block" size="58"/></td></tr>\n')
	replot.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
	replot.append('</table>\n')
	replot.append('</form>\n')
	replot.append('<p>The latest block: {} was found {} seconds ago at difficulty {}</p>\n'.format(str(mylatest[0]),str(int(mylatest[1])),str(mylatest[2])))
	replot.append('<p>Click on a block number to get transaction details</p>\n')
	replot.append(extext)
	replot.append('<table style="font-size: 70%">\n')
	replot.append('<tr>\n')
	replot.append('<td><b>Block</b></td>\n')
	replot.append('<td><b>Timestamp</b></td>\n')
	replot.append('<td><b>From</b></td>\n')
	replot.append('<td><b>To</b></td>\n')
	replot.append('<td><b>Amount</b></td>\n')
	replot.append('<td><b>Transaction ID (txid)</b></td>\n')
	replot.append('<td><b>Fee</b></td>\n')
	replot.append('<td><b>Reward</b></td>\n')
	replot.append('<td><b>Openfield</b></td>\n')
	replot.append('</tr>\n')
	replot = replot + view
	replot.append('</table>\n')
	replot.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	replot.append('</center>\n')
	replot.append('</body>\n')
	replot.append('</html>')
	
	html1 = "" + str(''.join(replot))

	return html1.encode("utf-8")

@app.route('/sponsorinfo')
def sponsorinfo():

	#initial = my_head('table, th, td {border: 0;}')
	initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')

	initial.append('<table ><tbody><tr>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">\n')
	initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
	initial.append('<h2>Sponsorship Information</h2>\n')
	initial.append('<p>To sponsor and have your weblink and logo appear on the Home page, send at least 1 Bismuth to:</p>\n')
	initial.append('<p><b>{}</b></p>\n'.format(myaddress))
	initial.append('<p>The current rate is {} blocks per Bismuth sent</p>\n'.format(str(int(myrate))))
	initial.append('<p></p>')
	initial.append('<p>When you send your payment include the openfield text: sponsor=your_url</p>\n')
	initial.append('<p>This tool will read the Opengraph properties: title, url, image and site_name - of your site to display its information</p>\n')
	initial.append('<p></p>')
	initial.append('<p><a href="http://ogp.me/" style="text-decoration:none;">Click here for more information about Opengraph</a></p>\n')		
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('</tr></tbody></table>\n')
	initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	initial.append('</center>\n')
	initial.append('</body>\n')
	initial.append('</html>')

	starter = "" + str(''.join(initial))

	return starter.encode("utf-8")

@app.route('/richest', methods=['GET'])
def richest_form():

	def_curr = "0"
	rawall = richones()
	all = []
	conv_curr = cmc_vals[int(def_curr)]
	
	for r in rawall:
		all.append((r[0],float(r[1]),r[2]))
			
	all = sorted(all, key=lambda address: address[1], reverse=True)
	
	view = []
	i = 0
	j = 1
	for x in all:
		thisrich = str(x[0])
		if len(thisrich) == 56:
			if j % 2 == 0:
				color_cell = "white"
			else:
				color_cell = "#E8E8E8"
			amt = "{:.8f}".format(x[1])
			if amt == "0.00000000" or amt == "-0.00000000":
				pass
			else:
				view.append("<tr bgcolor ='{}'>".format(color_cell))
				view.append("<td>{}</td>".format(str(j)))
				view.append("<td>{}</td>".format(str(x[0])))
				view.append("<td>{}</td>".format(str(x[2])))
				view.append("<td>{:.8f}</td>".format(x[1]))
				view.append("<td>{:.2f}</td>".format((x[1]*conv_curr)))				
				j = j+1
				view.append("</tr>\n")
		i = i+1
		
	lister = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
	lister.append('<h2>Bismuth Rich List</h2>\n')
	lister.append('<p><b>List of all Bismuth addresses with more than {} BIS</b></p>\n'.format(str(bis_limit)))
	lister.append('<p>Note: this page may be up to 45 mins behind</p>\n')
	lister.append('<p></p>\n')
	lister.append('<form method="post" action="/richest">\n')
	lister.append('<table>\n')
	lister.append('<tr><th><label for="my_curr">Choose currency</label></th>')
	lister.append('<td><select name="my_curr">\n')
	lister.append('<option value="0">BTC</option>\n')
	lister.append('<option value="1">USD</option>\n')
	lister.append('<option value="2">EUR</option>\n')
	lister.append('<option value="3">GBP</option>\n')
	lister.append('<option value="4">CNY</option>\n')
	lister.append('<option value="5">AUD</option>\n')
	lister.append('</select></td></tr>\n')
	lister.append('<tr><th><label for="Submit Query">Click Go</label></th><td><button id="Submit Query" name="Submit Query">Go</button></td></tr>\n')
	lister.append('</table>\n')
	lister.append('</form>\n')
	lister.append('<table style="width:65%" bgcolor="white">\n')
	lister.append('<p></p>\n')
	lister.append('<tr>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Rank</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Address</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Alias</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Balance (BIS)</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Balance ({})</b></td>\n'.format(disp_curr[int(def_curr)]))
	lister.append('</tr>\n')
	lister = lister + view
	lister.append('</table>\n')
	lister.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	lister.append('<p>Price information courtesy of coinmarketcap.com</p>')
	lister.append('</center>\n')
	lister.append('</body>\n')
	lister.append('</html>')

	html = "" + str(''.join(lister))

	return html.encode("utf-8")

@app.route('/richest', methods=['POST'])
def richest_result():

	try:
		def_curr = request.form.get('my_curr')
	except:
		def_curr = "0"
	rawall = richones()
	all = []
	conv_curr = cmc_vals[int(def_curr)]
	
	for r in rawall:
		all.append((r[0],float(r[1]),r[2]))
			
	all = sorted(all, key=lambda address: address[1], reverse=True)
	
	view = []
	i = 0
	j = 1
	for x in all:
		thisrich = str(x[0])
		if len(thisrich) == 56:
			if j % 2 == 0:
				color_cell = "white"
			else:
				color_cell = "#E8E8E8"
			amt = "{:.8f}".format(x[1])
			if amt == "0.00000000" or amt == "-0.00000000":
				pass
			else:
				view.append("<tr bgcolor ='{}'>".format(color_cell))
				view.append("<td>{}</td>".format(str(j)))
				view.append("<td>{}</td>".format(str(x[0])))
				view.append("<td>{}</td>".format(str(x[2])))
				view.append("<td>{:.8f}</td>".format(x[1]))
				view.append("<td>{:.2f}</td>".format((x[1]*conv_curr)))				
				j = j+1
				view.append("</tr>\n")
		i = i+1
	
	lister = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
	lister.append('<h2>Bismuth Rich List</h2>\n')
	lister.append('<p><b>List of all Bismuth address balances</b></p>\n')
	lister.append('<p>Note: this page may be up to 45 mins behind</p>\n')
	lister.append('<p></p>\n')
	lister.append('<form method="post" action="/richest">\n')
	lister.append('<table>\n')
	lister.append('<tr><th><label for="my_curr">Choose currency</label></th>')
	lister.append('<td><select name="my_curr">\n')
	lister.append('<option value="0">BTC</option>\n')
	lister.append('<option value="1">USD</option>\n')
	lister.append('<option value="2">EUR</option>\n')
	lister.append('<option value="3">GBP</option>\n')
	lister.append('<option value="4">CNY</option>\n')
	lister.append('<option value="5">AUD</option>\n')
	lister.append('</select></td></tr>\n')
	lister.append('<tr><th><label for="Submit Query">Click Go</label></th><td><button id="Submit Query" name="Submit Query">Go</button></td></tr>\n')
	lister.append('</table>\n')
	lister.append('</form>\n')
	lister.append('<table style="width:65%" bgcolor="white">\n')
	lister.append('<p></p>\n')
	lister.append('<tr>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Rank</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Address</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Alias</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Balance (BIS)</b></td>\n')
	lister.append('<td bgcolor="#D0F7C3"><b>Balance ({})</b></td>\n'.format(disp_curr[int(def_curr)]))
	lister.append('</tr>\n')
	lister = lister + view
	lister.append('</table>\n')
	lister.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	lister.append('</center>\n')
	lister.append('</body>\n')
	lister.append('</html>')

	html = "" + str(''.join(lister))

	return html.encode("utf-8")
	
@app.route('/apihelp')
def apihelp():

	#initial = my_head('table, th, td {border: 0;}')
	initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')

	initial.append('<table ><tbody><tr>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">\n')
	initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
	initial.append('<h2>API Help</h2>\n')
	initial.append('<p><b>Webtools includes a public API returning various JSON results</p>\n')
	initial.append('<p>The general format of a query is: http://{}/api/parameter1/parameter2</b></p>\n'.format(myhost))
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: stats</p>\n')
	initial.append('<p align="left">--->Parameter2: circulation <i>(gets the total number of Bismuth in circulation)</i></p>\n')
	initial.append('<p align="left">--->Parameter2: latestblock <i>(gets information about the last block found)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: address</p>\n')
	initial.append('<p align="left">--->Parameter2: input a bismuth address <i>(gets a summary of information about a Bismuth address)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: getall</p>\n')
	initial.append('<p align="left">--->Parameter2: input a bismuth address <i>(gets a limited list of transactions against a Bismuth address)</i></p>\n')
	initial.append('<p align="left"><i>List is limited to {} transactions</i></p>\n'.format(str(mydisplay)))
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: block</p>\n')
	initial.append('<p align="left">--->Parameter2: input a block number <i>(gets information about a Bismuth block)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: hash</p>\n')
	initial.append('<p align="left">--->Parameter2: input a hash value <i>(gets information about a Bismuth hash)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: richlist</p>\n')
	initial.append('<p align="left">--->Parameter2: input a number or the word all <i>(gets a list of top Bismuth wallets to the number specified (or all) sorted by wallet balance)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: miners</p>\n')
	initial.append('<p align="left">--->Parameter2: input a number or the word all <i>(gets a list of the top Bismuth miners to the number specified (or all) sorted by blocks found)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: aminer</p>\n')
	initial.append('<p align="left">--->Parameter2: input a miner address <i>(gets more information about a specific Bismuth miner)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: transaction</p>\n')
	initial.append('<p align="left">--->Parameter2: input a block number and amount separated by an = sign <i>(gets information about transaction)</i></p>\n')
	initial.append('<p></p>\n')
	initial.append('<p align="left">Parameter1: diffhist</p>\n')
	initial.append('<p align="left">--->Parameter2: number of blocks, greater than 10 <i>(gets the difficulty history for a specific number of previous blocks)</i></p>\n')
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('</tr></tbody></table>\n')
	initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	initial.append('</center>\n')
	initial.append('</body>\n')
	initial.append('</html>')

	starter = "" + str(''.join(initial))

	return starter.encode("utf-8")
	
@app.route('/charts')
def mycharts():

	#initial = my_head('table, th, td {border: 0;}')
	initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')

	initial.append('<table ><tbody><tr>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">\n')
	initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
	initial.append('<h2>Information Charts</h2>\n')
	initial.append('<p></p>')
	initial.append('<h3><a href="/diff_chart">Difficulty Chart</a></h3>\n')		
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial.append('<p></p>')
	initial.append('</td>\n')
	initial.append('</tr></tbody></table>\n')
	initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2018</p>')
	initial.append('</center>\n')
	initial.append('</body>\n')
	initial.append('</html>')

	starter = "" + str(''.join(initial))

	return starter.encode("utf-8")
	
@app.route('/details')
def detailinfo():

	try:
		getdetail = request.args.get('mydetail')
	except:
		getdetail = None
		
	#print(getdetail)

	if getdetail:
		m_stuff = getdetail.split(":")
		#print(m_stuff)
		
		conn = sqlite3.connect(bis_root)
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT * FROM transactions WHERE block_height = ? AND address = ? AND recipient = ? AND amount = ?;", (m_stuff[0],m_stuff[1],m_stuff[2],m_stuff[3]))

		m_detail = c.fetchone()
		#print(m_detail)
		c.close()
		conn.close()
		
		if m_detail:
		
			d_block = str(m_detail[0])
			d_time = str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(m_detail[1]))))
			d_from = str(m_detail[2])
			d_to = str(m_detail[3])
			d_amount = str(m_detail[4])
			d_sig = str(m_detail[5])
			d_txid = d_sig[:56]
			d_pub = str(m_detail[6])
			d_hash = str(m_detail[7])
			d_fee = str(m_detail[8])
			d_reward = str(m_detail[9])
			d_open = str(m_detail[11][:1000])
			
		else:
			
			d_block = "Not Found"
			d_time = ""
			d_from = ""
			d_to = ""
			d_amount = ""
			d_sig = ""
			d_txid = ""
			d_pub = ""
			d_hash = ""
			d_fee = ""
			d_reward = ""
			d_open = ""
			
	else:
	
		d_block = "Not Found"
		d_time = ""
		d_from = ""
		d_to = ""
		d_amount = ""
		d_sig = ""
		d_txid = ""
		d_pub = ""
		d_hash = ""
		d_fee = ""
		d_reward = ""
		d_open = ""
	
	return render_template('detail.html', ablock=d_block, atime=d_time, afrom=d_from, ato=d_to, aamount=d_amount, asig=d_sig, atxid=d_txid, apub=d_pub, ahash=d_hash, afee=d_fee, areward=d_reward, aopen=d_open)
	
@app.route('/api/<param1>/<param2>', methods=['GET'])
def handler(param1, param2):

	if param1 == "stats":
		if param2 == "circulation":
			x = getcirc()
			return json.dumps({'circulation':str(x)}), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

		elif param2 == "latestblock":
			x = latest()
			y = "%.2f" % x[1]
			z = str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[4]))))
			d = {'found':z,'height':str(x[0]),'age':str(y),'difficulty':str(x[2]),'finder':str(x[3]),'blockhash':str(x[5]),'nonce':str(x[6])}
			return json.dumps(d), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid request"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
	elif param1 == "address":
		getaddress = str(param2)
		if s_test(getaddress):
			myxtions = refresh(getaddress,1)
			if float(myxtions[4]) > 0:
				x = {'address':getaddress,'credits':myxtions[0],'debits':myxtions[1],'rewards':myxtions[2],'fees':myxtions[3],'balance':myxtions[4]}
				return json.dumps(x), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				r = "{} has a zero balance....".format(getaddress)
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid address"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
	elif param1 == "getall":
		getaddress = str(param2)
		if not getaddress or not s_test(getaddress):
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			all = []
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			if mydisplay == 0:
				c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC;", (getaddress,getaddress))
			else:
				c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC LIMIT ?;", (getaddress,getaddress,str(mydisplay)))
			all = c.fetchall()
			c.close()
			conn.close()
			if not all:
				r = "address does not exist or invalid address"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				y.append({"address":getaddress,"limit":"{} records".format(str(mydisplay))})
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"fee":str(b[8]),"reward":str(b[9]),"keep":str(b[10]),"openfield":str(b[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
	elif param1 == "getlimit":
		getlimit = str(param2)
		
		if "=" in getlimit:	
			getaddress = getlimit.split("=")[0]
			mylimit = getlimit.split("=")[1]
		else:
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}		
		
		if not getaddress or not s_test(getaddress):
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			all = []
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC LIMIT ?;", (getaddress,getaddress,mylimit))
			all = c.fetchall()
			c.close()
			conn.close()
			if not all:
				r = "address does not exist or invalid address"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				y.append({"address":getaddress,"limit":"{} records".format(mylimit)})
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"hash":str(b[7]),"fee":str(b[8]),"reward":str(b[9]),"keep":str(b[10]),"openfield":str(b[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

	elif param1 == "block":
		myblock = str(param2)
		if not myblock or not myblock.isalnum():
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			all = []
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_height = ?;", (myblock,))
			all = c.fetchall()

			c.close()
			conn.close()

			if not all:
				r = "block does not exist or invalid block"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				y.append({"blocknumber":myblock,"blockhash":str(all[0][7])})
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"hash":str(b[7]),"fee":str(b[8]),"reward":str(b[9]),"keep":str(b[10]),"openfield":str(b[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

	elif param1 == "hash":
		gethash = str(param2)
		if not s_test(gethash):
			r = "invalid data"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			all = []
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_hash = ?;", (gethash,))
			all = c.fetchall()
			c.close()
			conn.close()
			if not all:
				r = "hash does not exist or invalid data"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				y.append({"blockhash":gethash,"blocknumber":str(all[0][0])})
								
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"hash":str(b[7]),"fee":str(b[8]),"reward":str(b[9]),"keep":str(b[10]),"openfield":str(b[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
	elif param1 == "richlist":
		rich_num = str(param2)
		nog = True
		ra = richones()
		rag =[(r[0],float(r[1]),r[2]) for r in ra]
		rag = sorted(rag, key=lambda address: address[1], reverse=True)
		
		if rich_num.isdigit():
			rich_num = int(rich_num)
			if rich_num > len(rag):
				rich_num = len(rag)
		elif rich_num == "all":
			rich_num = len(rag)
		else:
			nog = False
		
		nt = range(rich_num)
			
		if nog:
			y = [{"rank":str(g+1),"address":str(rag[g][0]),"alias":str(rag[g][2]),"balance":('%.8f' % rag[g][1])} for g in nt]
			return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid request"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			
	elif param1 == "miners":
		miner_num = str(param2)
		mog = True
		ma = miners()
		
		if miner_num.isdigit():
			miner_num = int(miner_num)
			if miner_num > len(ma):
				miner_num = len(ma)
		elif miner_num == "all":
			miner_num = len(ma)
		else:
			mog = False
		
		nt = range(miner_num)
			
		if mog:
			y = [{"rank":str(g+1),"address":str(ma[g][0]),"blocks":str(ma[g][3]),"rewards":str(ma[g][4]),"alias":str(ma[g][5])} for g in nt]
			return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid request"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			
	elif param1 == "aminer":
		getaddress = str(param2)
		if s_test(getaddress):
			m_info = bgetvars(getaddress)
			if m_info:
				x = {'address':str(m_info[0]),'latestblock':str(m_info[1]),'firstblock':str(m_info[2]),'total':str(m_info[3]),'rewards':str(m_info[4])}
				return json.dumps(x), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}				
			else:
				r = "{} is not a miner....".format(getaddress)
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid address"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			
	elif param1 == "getsponsor":
		getaddress = str(param2)
		if not getaddress or not s_test(getaddress):
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:

			sponsor_result = sponsor_list(getaddress,14400)
			
			if not sponsor_result:
				r = "oops there was a problem getting a sponsor url"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
			
				x_top = len(sponsor_result) -1
				x_go = random.randint(0,x_top)
				ts = sponsor_result[x_go]
				
				y = []

				y.append({"title":ts[0],"image":ts[1],"url":ts[2],"description":ts[3],"sitename":ts[6]})
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

	elif param1 == "toolsaddress":

		if str(param2) == "toolsaddress":
			t_result = get_open("403786","toolsaddress")
			#print(t_result)
			
			xo = t_result[2]
			xi = t_result[3]
			
			if xo == xi:
						
				y = []
				y.append({'toolsaddress':str(xo)})
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				r = "invalid data entered"
				e = {"error":r}
				return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}			
		else:
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			
	elif param1 == "transaction":
		get_trans = str(param2)
		
		if "=" in get_trans:	
			getblock = get_trans.split("=")[0]
			myamnt = get_trans.split("=")[1]
		else:
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}		
		
		if not getblock or not getblock.isalnum():
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			
			conn = sqlite3.connect(bis_root)
			conn.text_factory = str
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_height = ? AND amount = ?;", (getblock, myamnt))
			td = c.fetchone()
			c.close()
			conn.close()

			if not td:
				r = "transaction does not exist or invalid transaction"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = {"block":str(td[0]),"timestamp":str(td[1]),"from":str(td[2]),"to":str(td[3]),"amount":str(td[4]),"hash":str(td[7]),"fee":str(td[8]),"reward":str(td[9]),"keep":str(td[10]),"openfield":str(td[11])}
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
	elif param1 == "diffhist":
		diff_num = str(param2)
		dog = True
		
		conn = sqlite3.connect(bis_root)
		conn.text_factory = str
		c = conn.cursor()
				
		if diff_num.isdigit():
			if int(diff_num) > 10:
				c.execute("SELECT * FROM misc ORDER BY block_height DESC LIMIT ?;", (diff_num,))
				d_result = c.fetchall()
				b = []
				d = []
				d_result = list(reversed(d_result))
				for v in d_result:
					b.append(v[0])
					d.append(float(v[1]))
		
		else:
			dog = False
		
		c.close()
		conn.close()

		if dog:
			y = [b,d]
			return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid request value must be more than 10"
			e = {"error":r}
			return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

	else:
		r = "invalid request"
		e = {"error":r}
		return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

urls = (
    '/', 'index',
	'/minerquery', 'minerquery',
	'/ledgerquery', 'ledgerquery',
	'/richest', 'richest',
	'/sponsorinfo', 'sponsorinfo',
	'/api', 'api',
	'/apihelp', 'API',
	'/charts', 'Charts',
	'/diff_chart', 'Difficulty',
	'/details', 'Details'
)

if __name__ == "__main__":

	background_thread = threading.Thread(target=buildtoolsdb)
	background_thread.daemon = True
	background_thread.start()
	logging.info("Databases: Start Thread")
	
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(8080)
	IOLoop.instance().start()
	
	#app.run()
