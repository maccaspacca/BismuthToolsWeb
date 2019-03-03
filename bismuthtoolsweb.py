# Bismuth Tools Web
# Version 6.2.5
# Date 26/02/2019
# Copyright The Bismuth Foundation 2016 to 2019
# Author Maccaspacca

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.websocket
import tornado.httpserver
import tornado.web
from random import randint #Random generator

from flask import Flask, request
from flask import Markup
from flask import render_template
app = Flask(__name__)

import json, sqlite3, time, re, os, socks, connections, bisurl, pyqrcode, datetime, calendar
import threading
from bs4 import BeautifulSoup
import log, random, platform, requests
import configparser as cp
from urllib.request import Request, urlopen
from decimal import *
from glob import glob
	
# globals
global my_os
global bis_root
global myaddress
global myrate
global disp_curr

disp_curr = ["BTC","USD","EUR","GBP","CNY","AUD"]

app_log = log.log("toolsdb.log","WARNING", "yes")

app_log.info("logging initiated")

config = cp.ConfigParser()
config.readfp(open(r'toolsconfig.ini'))
app_log.info("Reading config file.....")
myaddress = config.get('My Sponsors', 'address')
myrate = float(config.get('My Sponsors', 'rate'))
myhost = config.get('My Sponsors', 'hostname')
try:
	mydisplay = int(config.get('My Sponsors', 'display'))
except:
	mydisplay = 0
db_root = config.get('My Bismuth', 'dbpath')
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
	topia = "8b447aa5845a2b6900589255b7d811a0a40db06b9133dcf9569cdfa0" # cryptopia address
try:
	diff_ch = int(config.get('My Charts', 'diff'))
except:
	diff_ch = 50
try:
	bis_mode = config.get('My Bismuth', 'bis_mode')
except:
	bis_mode = "live"
try:
	ip = config.get('My Bismuth', 'node_ip')
except:
	ip = "127.0.0.1"
	
app_log.info("Config file read completed")
config = None

if bis_mode == "testnet":
	port = "2829"
	db_name = "test.db"
else:
	port = "5658"
	db_name = "ledger.db"
	
my_os = platform.system()
my_os = my_os.lower()

bis_root = "{}{}".format(db_root,db_name)

if "linux" in my_os:
	bis_root = os.path.expanduser('{}'.format(bis_root))
	db_root = os.path.expanduser('{}'.format(db_root))
elif "windows" in my_os:
	pass
else: # if its not windows then probably a linux or unix variant
	pass
	
print("Bismuth DB path = {}".format(bis_root))
app_log.info("Bismuth DB path = {}".format(bis_root))
print("Bismuth DB root = {}".format(db_root))
app_log.info("Bismuth DB root = {}".format(db_root))

db_hyper = False

if os.path.isfile('{}hyper.db'.format(db_root)):
	db_hyper = True
	hyper_root = '{}hyper.db'.format(db_root)
else:
	hyper_root = bis_root # just in case
	
app_log.info("Hyper.db exists = {}".format(db_hyper))
print("Hyper.db exists = {}".format(db_hyper))
app_log.info("Hyper.db path = {}".format(hyper_root))
print("Hyper.db path = {}".format(hyper_root))

# Classes start

wport = 8880 #Websocket Port
timeInterval= 5000 #Milliseconds

class WSHandler(tornado.websocket.WebSocketHandler):
	#check_origin fixes an error 403 with Tornado
	#http://stackoverflow.com/questions/24851207/tornado-403-get-warning-when-opening-websocket
	def check_origin(self, origin):
		return True

	def open(self):
		#Send message periodic via socket upon a time interval
		self.callback = PeriodicCallback(self.send_values, timeInterval)
		self.callback.start()

	def send_values(self):
		
		self.thismessage = self.mpgetjson()

		for response in self.thismessage:
			smessage = response
			self.write_message(smessage)

	def on_message(self, message):
		pass

	def on_close(self):
		self.callback.stop()
		
	def mpgetjson(self):
		#ask for mempool
	
		s = socks.socksocket()
		s.settimeout(10)
		s.connect((ip, int(port)))

		connections.send(s, "mpgetjson", 10)
		response_list = connections.receive(s, 10)
		
		send_back = []
		
		if response_list:
		
			t = "<br>There are {} transactions in the mempool</br>".format(str(len(response_list)))
			# send_back.append(t)
		
			for response in response_list:
				address = response['address']
				recipient = response['recipient']
				amount = response['amount']
				txid = response['signature'][:56]
				operation = response['operation']
				openfield = response['openfield']
				
				t = t + "<br><b>Address:</b> {}, Recipient: {}, Amount: {}, txid: {}, Operation: {}, Openfield: {}</br>".format(address,recipient,amount,txid,operation,openfield)
			send_back.append(t)
		else:
			t = "Mempool Empty"
			send_back.append(t)
			
		s.close()
		
		return send_back
		#ask for mempool

# End Classes


def get_cmc_info(alt_curr):

	ch = alt_curr.lower()

	try:
		t = "https://api.coingecko.com/api/v3/coins/bismuth?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
		r = requests.get(t)
		x = r.text
		y = json.loads(x)
		try:
			c_btc = "{:.8f}".format(float(y['market_data']['current_price']['btc']))
			c_usd = "{:.3f}".format(float(y['market_data']['current_price']['usd']))
			c_cus = "{:.3f}".format(float(y['market_data']['current_price'][ch]))
			#print( y )
			s = "<p><b> LATEST PRICES: BTC = {} | USD = {} | {} = {}</b></p>".format(c_btc,str(c_usd),alt_curr,str(c_cus))
		except:
			c_btc = ""
			c_usd = ""
			c_cus = ""
			s = "<p><b></b></p>"
		
	except requests.exceptions.RequestException as e:
		s = "<p><b>Price Error: {}</b></p>".format(e)

	return s
	
def get_cmc_val(alt_curr):

	ch = alt_curr.lower()

	try:
		t = "https://api.coingecko.com/api/v3/coins/bismuth?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
		r = requests.get(t)
		x = r.text
		y = json.loads(x)
		try:
			s = float(y['market_data']['current_price'][ch])
		except:
			s = 0.00000001
		
	except:
		s = 0.00000001

	return s

	
def display_time(seconds, granularity=2):

	intervals = (
		('weeks', 604800),  # 60 * 60 * 24 * 7
		('days', 86400),    # 60 * 60 * 24
		('hours', 3600),    # 60 * 60
		('minutes', 60),
		('seconds', 1),
		)

	result = []

	for name, count in intervals:
		value = seconds // count
		if value:
			seconds -= value * count
			if value == 1:
				name = name.rstrip('s')
			result.append("{} {}".format(value, name))
	return ', '.join(result[:granularity])
	
def status_me():

	try:
		s = socks.socksocket()
		s.settimeout(10)
		s.connect((ip, int(port)))
		
		# Node status
		connections.send(s, "statusjson", 10)
		status_resp = connections.receive(s, 10)
		# Node status
				
		try:
			w_version = status_resp['walletversion']
			p_version = status_resp['protocolversion']
			w_cnx = status_resp['connections']
			w_uptime = status_resp['uptime']
			w_cons = status_resp['consensus_percent']
			w_blk = status_resp['consensus']
		except:
			w_version = ""
			p_version = ""
			w_cnx = ""
			w_uptime = "0"
			w_cons = "0"
			w_blk = ""
	except:
		w_version = ""
		p_version = ""
		w_cnx = ""
		w_uptime = "0"
		w_cons = "0"
		w_blk = ""
		
	n_up = display_time(int(w_uptime),4)
		
	node_info = "<b><p>Node uptime: {}</p><p>Running {} and software version {}</p>\n".format(n_up,p_version,w_version)
	node_info = node_info + "<p>Consensus is {} % at block number {} with {} connections</b></p>\n".format(str(int(w_cons)),w_blk,w_cnx)
	
	return node_info

	
def latest():

	try:
		s = socks.socksocket()
		s.settimeout(10)
		s.connect((ip, int(port)))
		connections.send(s, "blocklast", 10)
		block_get = connections.receive(s, 10)
		#print(block_get)
		
		# check difficulty
		connections.send(s, "diffget", 10)
		diff = connections.receive(s, 10)
		# check difficulty
	
		try:
			db_block_height = str(block_get[0])
			db_timestamp_last = block_get[1]
			db_block_finder = block_get[2]
			db_block_hash = block_get[7]
			db_block_txid = block_get[5][:56]
			db_block_open = block_get[11]
			time_now = str(time.time())
			last_block_ago = (float(time_now) - float(db_timestamp_last))#/60
			#last_block_ago = '%.2f' % last_block_ago
			diff_block_previous = '%.2f' % float(diff[1])
		except:
			db_block_height = ""
			db_timestamp_last = ""
			db_block_finder = ""
			db_block_hash = ""
			db_block_txid = ""
			db_block_open = ""
			last_block_ago = ""
			diff_block_previous = ""
		#print("connected")
		s.close()
	except:
		print("No connection")

	app_log.info("Latest block queried: {}".format(str(db_block_height)))

	return db_block_height, last_block_ago, diff_block_previous, db_block_finder, db_timestamp_last, db_block_hash, db_block_open, db_block_txid
	
def get_block_time(my_hist):

	lb_tick = latest()
	lb_height = lb_tick[0]
	lb_stamp = lb_tick[4]
	sb_height = int(lb_height) - my_hist
	
	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT timestamp,block_height FROM transactions WHERE reward !=0 and block_height >= ?;",(str(sb_height),))
	result = c.fetchall()

	l = []
	y = 0
	for x in result:
		if y == 0:
			ts_difference = 0
		else:
			ts_difference = float(x[0]) - float(y)
		ts_block = x[1]
		#print(str(x[1])+" "+str(ts_difference))
		tx = (ts_block,ts_difference)
		l.append(tx)
		y = x[0]

	return l
	

def getmeta(this_url):
# This module attempts to get Open Graph information for the sponsor site_name
# If this fails it attempts to use the "name" property before just filling the info with the url

	app_log.info("Running getmeta for {}".format(this_url))

	this_property = ("og:title","og:image","og:url","og:description","og:site_name")
	oginfo = []
	
	req = Request(this_url, headers={'User-Agent': 'Mozilla/5.0'})
	
	url = urlopen(req)
		
	webpage = url.read()
	
	soup = BeautifulSoup(webpage, "html.parser")
	
	for prop in this_property:
		temp_tag = soup.find("meta", {"property": prop})
		if temp_tag is not None:
			oginfo.append(str(temp_tag["content"]))
		else:
			temp_tag = soup.find("meta", {"name": prop})
			if temp_tag is not None:
				oginfo.append(str(temp_tag["content"]))
			else:
				ex_prop = prop.split(":")[1]
				ex_tag = soup.find("meta", {"name": ex_prop})
				if ex_tag is not None:
					oginfo.append(str(ex_tag["content"]))
				else:
					oginfo.append("")
	
	app_log.info("OGS: {}".format(oginfo))
	return oginfo

def i_am_first(my_first,the_address):

	# Is the suggested alias the first one for this address

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

	app_log.info("Tools DB: Check miner name result: Address {} = {}".format(str(myaddress),goodname))
		
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
	if myaddress == "8b447aa5845a2b6900589255b7d811a0a40db06b9133dcf9569cdfa0":
		goodname = "Cryptopia Exchange"

	#app_log.info("Tools DB: Check alias result: Address {} = {}".format(str(myaddress),goodname))

	return goodname
	
# get and process address information

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
		
	r_alias = get_alias(testAddress)
	
	get_stuff = ["{:.8f}".format(credit),"{:.8f}".format(debit),"{:.8f}".format(rewards),"{:.8f}".format(fees),"{:.8f}".format(balance),t_max, t_min, b_count, r_alias]
		
	return get_stuff
	
def sponsor_list(thisaddress,thisrate):

	#app_log.info("sponsor address: {}".format(thisaddress))

	mysponsors = []

	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE recipient = ? AND instr(openfield, 'sponsor=') > 0;",(thisaddress,))
	mysponsors = c.fetchall()
	#app_log.warning(mysponsors)
	c.close()

	the_sponsors = []

	for dudes in mysponsors:

		dud = dudes[11].split("sponsor=")

		try:
			temp_block = dudes[0]
			temp_paid = float(dudes[4])
			max_block = temp_block + (int(round(temp_paid * thisrate)) + 100)
			
			#app_log.info("Max block: {}".format(str(max_block)))

			latest_block = latest()
			
			#app_log.info("Latest block: {}".format(str(latest_block[0])))
						
			if int(latest_block[0]) < max_block:
				app_log.info("sponsors - checking ogs")
				
				temp_ogs = getmeta(str(dud[1]))
		
				the_sponsors.append((temp_ogs[0],temp_ogs[1],temp_ogs[2],temp_ogs[3],str(max_block),str(temp_block),temp_ogs[4]))
			else:
				pass
			
		except:
			pass

	if not the_sponsors:
		the_sponsors.append(("Bismuth","static/final.png","http://bismuth.cz/","In the truly free world, there are no limits","5000000","68924","Bismuth"))
			
	return the_sponsors
	
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
	
	c.execute("SELECT sum(amount) FROM transactions WHERE address = 'Hypernode Payouts';")
	
	allmno = c.fetchone()[0]
	
	if not allhyp:
		allhyp = 0
	if not alldev:
		alldev = 0
	if not allmno:
		allmno = 0

	allcirc = float(allcirc) + float(alldev) + float(allhyp) + float(allmno)
	
	allcirc = "{:.8f}".format(allcirc)

	c.close()
	conn.close()
	
	print(allcirc)
	
	return allcirc
	
def updatedb():
	x = status_me()

	print("Updating database.....wait")
	
	app_log.info("Tools DB: Rebuild")

	# create empty tools database
	tools = sqlite3.connect('temptools.db')
	tools.isolation_level = None
	tools.text_factory = str
	m = tools.cursor()
	m.execute("CREATE TABLE IF NOT EXISTS richlist (address, balance, alias)")
	m.execute("CREATE TABLE IF NOT EXISTS minerlist (address, blatest, bfirst, blockcount, treward, mname)")
	m.execute("CREATE TABLE IF NOT EXISTS sponsorlist (title, image, url, description, end, paid, name)")
	tools.commit()

	app_log.info("Tools DB: Creating or updating tools database")
		
	app_log.info("Tools DB: Getting info.....")

# sponsors ///////////////////////////////////////////////////

	app_log.info("Tools DB: Getting up to date list of sponsors.....")

	the_sponsors = sponsor_list(myaddress,myrate)
			
	app_log.info("Tools DB: Inserting sponsor information into database.....")
			
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
	
	app_log.info("Tools DB: getting richlist and minerlist information.....")
		
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
	app_log.info("Tools DB: Done !")
	
	return True

def buildtoolsdb():

	global home_stats
	global cmc_vals
	global circ_val
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
	circ_val = getcirc()
	
	updatedb()
	
	i = 0
	
	while True:
	
		print("Price info updated: Waiting for 5 minutes.......")
	
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
		circ_val = getcirc()
		for f in glob("static/qr*.png"):
			os.remove(f)
		i +=1
		if i == 6:
			bobble = updatedb()
			print("Tools DB updated: Waiting for 30 minutes.......")
			i = 0

def checkstart():

	if not os.path.exists('tools.db'):
		# create empty miners database
		app_log.info("Tools DB: Create New as none exists")
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

# get latest transactions

def getall():

	if db_hyper:
		conn = sqlite3.connect(hyper_root)
	else:
		conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?;", ((front_display*2),))
	un_all = c.fetchall()
	
	sor_all = sorted(un_all, key=lambda tup: abs(tup[0]), reverse=True)
	
	myall = sor_all[:49]
	
	c.close()
	conn.close()

	return myall
	
# get latest transactions
	
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

	app_log.info("Tools DB: Get mining addresses from tools.db")
	conn = sqlite3.connect('tools.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM minerlist ORDER BY blockcount DESC;")
	miner_result = c.fetchall()
	c.close()
	conn.close()

	return miner_result

def richones():

	app_log.info("Tools DB: Get rich addresses from tools.db")
	conn = sqlite3.connect('tools.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM richlist ORDER BY balance DESC;")
	rich_result = c.fetchall()
	c.close()
	conn.close()

	return rich_result

def rev_alias(tocheck):

	a_addy = tocheck.split(":")
	t_addy = str(a_addy[1])
	#print(t_addy)

	try:
		conn = sqlite3.connect('tools.db')
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT address FROM richlist WHERE alias=?;", (t_addy,))
		d_addy = c.fetchone()
		
		if d_addy:
			r_addy = d_addy[0]
		else:
			c.execute("SELECT address FROM minerlist WHERE mname=?;", (t_addy,))
			e_addy = c.fetchone()
			
			if e_addy:
				r_addy = e_addy[0]
			else:				
				r_addy = "0"

		c.close()
		conn.close()
	except:
		r_addy = "0"
		
	print(r_addy)
		
	return str(r_addy)
	
	
def get_the_details(getdetail, get_addy):

	m_stuff = "{}%".format(str(getdetail))
	
	if db_hyper:
	
		conn = sqlite3.connect(hyper_root)
		conn.text_factory = str
		c = conn.cursor()
		c.execute("PRAGMA case_sensitive_like=OFF;")
		c.execute("SELECT * FROM transactions WHERE signature LIKE ?;", (m_stuff,))
		m_detail = c.fetchone()
		#print(m_detail)
		c.close()
		conn.close()
		
		if not m_detail:
		
			if get_addy:
		
				conn = sqlite3.connect(bis_root)
				conn.text_factory = str
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE address = ?;", (get_addy,))
				t_detail = c.fetchall()
				c.close()
				conn.close()

				x_detail = [sig for sig in t_detail if getdetail in sig[5]]
				
				m_detail = x_detail[0]
				
			else:
				conn = sqlite3.connect(bis_root)
				conn.text_factory = str
				c = conn.cursor()
				c.execute("PRAGMA case_sensitive_like=OFF;")
				c.execute("SELECT * FROM transactions WHERE signature LIKE ?;", (m_stuff,))
				m_detail = c.fetchone()
				#print(m_detail)
				c.close()
				conn.close()				

	else:
		conn = sqlite3.connect(bis_root)
		conn.text_factory = str
		c = conn.cursor()
		c.execute("PRAGMA case_sensitive_like=OFF;")
		c.execute("SELECT * FROM transactions WHERE signature LIKE ?;", (m_stuff,))
		m_detail = c.fetchone()
		#print(m_detail)
		c.close()
		conn.close()	
	
	return m_detail
	
	
def get_sponsor():

	try:
	
		app_log.info("Sponsors: Get sites from tools.db")
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
		
		app_log.info("Sponsors: {} was displayed".format(sponsor_result[x_go][2]))
	
	except:
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
	
	
#////////////////////////////////////////////////////////////
#                       MAIN APP
# ///////////////////////////////////////////////////////////


@app.route('/')
def home():

	currcoins = circ_val
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
						
		det_str = str(x[5][:56])
		det_str = det_str.replace("+","%2B")
		det_link = "/details?mydetail={}&myaddress={}".format(det_str,str(x[2]))
		thisview.append('<tr bgcolor ="{}">'.format(color_cell))
		if x[0] < 0:
			thisview.append('<td>{}</td>'.format(str(x[0])))
		else:
			thisview.append('<td><a href="{}">{}</a></td>'.format(det_link,str(x[0])))
		thisview.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))))))
		thisview.append('<td>{}</td>'.format(a_from)) # from
		thisview.append('<td>{}</td>'.format(a_to)) # to
		thisview.append('<td>{}</td>'.format(str(x[4])))
		thisview.append('<td>{}</td>'.format(str(x[5][:56])))
		thisview.append('<td>{}</td>'.format(str(x[8])))
		thisview.append('<td>{}</td>'.format(str(x[9])))
		thisview.append('</tr>\n')
		i = i+1		

	initial = []
	sponsor1 = get_sponsor()
	sponsor2 = get_sponsor()
	
	initial.append('<table ><tbody><tr>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial = initial + sponsor1
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">\n')
	initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
	initial.append('<h2>Welcome to the Bismuth Tools Web Edition</h2>\n')
	initial.append('<h3>Choose what you want to do next by clicking an option from the menu above</h3>\n')
	node_info = status_me()
	initial.append(node_info)
	initial.append('<p><b>There are {} Bismuth in circulation</b></p>\n'.format(str(currcoins)))
	initial.append('<h2>Last {} Transactions</h2>\n'.format(front_display))
	initial.append('</td>\n')
	initial.append('<td align="center" style="border:hidden;">')
	initial = initial + sponsor2
	initial.append('</td>\n')
	initial.append('</tr><tr>\n')
	initial.append('<td colspan="3" align="center" style="border:hidden;">\n')
	cmcstats = home_stats
	initial.append('{}'.format(cmcstats))
	initial.append('</td></tr>\n')
	initial.append('<tr><td colspan="3" align="center" style="border:hidden;">\n')
	initial.append('Price information courtesy of CoinGecko</td>\n')
	initial.append('</tr></tbody></table>\n')
	initial.append('<table style="font-size: 76%">\n')
	initial.append('<tr>\n')
	initial.append('<td><b>Block</b></td>\n')
	initial.append('<td><b>Timestamp</b></td>\n')
	initial.append('<td><b>From</b></td>\n')
	initial.append('<td><b>To</b></td>\n')
	initial.append('<td><b>Amount</b></td>\n')
	initial.append('<td><b>Transaction I.D.</b></td>\n')
	initial.append('<td><b>Fee</b></td>\n')
	initial.append('<td><b>Reward</b></td>\n')
	initial.append('</tr>\n')
	initial = initial + thisview
	initial.append('</table>\n')
	
	starter = "" + str(''.join(initial))
	
	return render_template('base.html', starter=starter)
	
@app.route('/diff_chart')
def d_chart():

	ttl = "Recent Bismuth Difficulty"
	lt = "line"
	conn = sqlite3.connect(bis_root)
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM misc ORDER BY block_height DESC LIMIT ?;", (diff_ch,))
	d_result = c.fetchall()
	#print(d_result)
	b = []
	d = []
	d_result = list(reversed(d_result))
	for v in d_result:
		b.append(v[0])
		d.append(float(v[1]))
	
	c.close()
	conn.close()	
	
	legend = 'Difficulty'

	return render_template('chart.html', values=d, labels=b, legend=legend, ttl=ttl, lt=lt)

@app.route('/time_chart')
def b_chart():

	ttl = "Recent Bismuth Blocktime"
	lt = "bar"
	b = []
	d = []
	d_result = get_block_time(120)
	#print(d_result)
	
	#d_result = list(reversed(d_result))

	for v in d_result:
		b.append(v[0])
		d.append(round(v[1],8))

	legend = 'Blocktime (seconds)'
	#print(d)

	return render_template('chart.html', values=d, labels=b, legend=legend, ttl=ttl, lt=lt)
	

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
		
	lister = []
	
	lister.append('<h2>Bismuth Miner Statistics</h2>\n')
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
	
	starter = "" + str(''.join(lister))
	
	return render_template('base.html', starter=starter)


@app.route('/ledgerquery', methods=['GET'])
def ledger_form():
		
	mylatest = latest()

	plotter = []
	
	plotter.append('<h2>Bismuth Ledger Query Tool</h2>\n')
	plotter.append('<p>Get a List of Transactions</p>\n')
	plotter.append('<form method="post" action="/ledgerquery">\n')
	plotter.append('<table>\n')
	plotter.append('<tr><th><label for="block">Enter a Block number, txid, hash, address or a: followed by alias</label></th><td><input type="text" id="block" name="block" size="68"/></td></tr>\n')
	plotter.append('<tr><th><label for="extra">Speed up older txid queries with a from Address (optional)</label></th><td><input type="text" id="extra" name="extra" size="68"/></td></tr>\n')
	plotter.append('<tr><th><label for="sdate">Start Date (optional)</label></th><td><input type="date" id="sdate" name="sdate" size="68"/> 00:00:00 hrs</td></tr>\n')
	plotter.append('<tr><th><label for="fdate">End Date (optional)</label></th><td><input type="date" id="fdate" name="fdate" size="68"/> 23:59:59 hrs</td></tr>\n')
	plotter.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
	plotter.append('</table>\n')
	plotter.append('</form>\n')
	#plotter.append('</p>\n')
	plotter.append('<p>Note: all queries are case sensitive</p>\n')
	plotter.append('<p>The latest block: {} was found {} seconds ago at difficulty {}</p>\n'.format(str(mylatest[0]),str(int(mylatest[1])),str(mylatest[2])))

	# Initial Form
	
	starter = "" + str(''.join(plotter))
	
	return render_template('base.html', starter=starter)


@app.route('/ledgerquery', methods=['POST'])
def ledger_query():
	
	mylatest = latest()
	
	a_display = False

	myblock = request.form.get('block')
	xdate = request.form.get('sdate')
	ydate = request.form.get('fdate')
	f_addy = request.form.get('extra')
	
	f_addy = f_addy.strip()
	
	if not f_addy:
		f_addy = "0"
	if not test(f_addy) == 1:
		f_addy = None

	if xdate:
		l_date = float(calendar.timegm(time.strptime(xdate, '%Y-%m-%d')))
	else:
		l_date = 1493640955.47
		
	if ydate:
		r_date = float(calendar.timegm(time.strptime(ydate, '%Y-%m-%d'))) + 86399
	else:
		r_date = mylatest[4]
	
	#print("Start date: {}".format(l_date))
	#print("End date: {}".format(r_date))

	r_block = myblock
	
	#Nonetype handling - simply replace with "0"
	
	if not myblock:
		myblock = "0"
		
	myblock = myblock.strip()
	
	if "f:" in myblock:
		a_display = True
		myblock = myblock.split(":")[1]
		#print(myblock)
		#print(a_display)
	
	if "a:" in myblock:
		myblock = rev_alias(myblock)
	
	my_type = test(myblock)
	
	if my_type == 3:
		myblock = "0"
		my_type = 2
	
	if my_type == 1:
		
		myxtions = refresh(myblock,1)
		#print(myxtions)
		
		if float(myxtions[0]) or float(myxtions[2]) > 0:
		
			if myxtions[8] == "":
				extext = "<p style='color:#08750A'><b>ADDRESS FOUND | Credits: {} | Debits: {} | Rewards: {} |".format(myxtions[0],myxtions[1],myxtions[2])
				extext = extext + " Fees: {} | BALANCE: {}</b></p>".format(myxtions[3],myxtions[4])
			else:
				extext = "<p style='color:#08750A'><b>ALIAS: {}</b></p>\n".format(myxtions[8])
				extext = extext + "<p style='color:#08750A'><b>ADDRESS FOUND | Credits: {} | Debits: {} | Rewards: {} |".format(myxtions[0],myxtions[1],myxtions[2])
				extext = extext + " Fees: {} | BALANCE: {}</b></p>".format(myxtions[3],myxtions[4])
			
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE (timestamp BETWEEN ? AND ?) AND (address = ? OR recipient = ?) ORDER BY timestamp DESC;", (l_date,r_date,str(myblock),str(myblock)))
			
			temp_all = c.fetchall()

			if mydisplay == 0 or a_display or l_date > 1493640955.47:
				all = temp_all
				a_display = False
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
				
				
			
				#conn = sqlite3.connect(bis_root)
				#c = conn.cursor()
				#c.execute("SELECT * FROM transactions WHERE instr(signature, ?) > 0;",(str(myblock),))

				#all = c.fetchall()
				
				#c.close()
				#conn.close()
				
				all = [get_the_details(str(myblock),f_addy)]
				
			if not all:				
				extext = "<p style='color:#C70039'>Nothing found for the address, txid or hash you entered - perhaps there has never been any transactions made?</p>"
			else:
				extext = "<p>Transaction found for the txid you entered</p>"
	
	if my_type == 2:
	
		if myblock == "0":
		
			all = []
		
		else:
		
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			c.execute("SELECT * FROM transactions WHERE block_height = ?;", (myblock,))

			all = c.fetchall()
		
			c.close()
			conn.close()
	
		if not all:
			extext = "<p style='color:#C70039'>Block, address, txid or hash not found. Maybe there has been no transactions, you entered bad data, or you entered nothing at all?</p>\n"
		else:
			pblock = int(myblock) -1
			nblock = int(myblock) +1
			extext = "<form action='/ledgerquery' method='post'><table><tr>\n"
			if pblock > 0:
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
			
		if bool(BeautifulSoup(str(x[11]),"html.parser").find()):
			x_open = "HTML NOT SHOWN HERE"
		else:
			x_open = str(x[11][:20])
		
		det_str = str(x[5][:56])
		det_str = det_str.replace("+","%2B")
		det_link = "/details?mydetail={}&myaddress={}".format(det_str,str(x[2]))
		view.append('<tr bgcolor ="{}">'.format(color_cell))

		if x[0] < 0:
			view.append('<td>{}</td>'.format(str(x[0])))
		else:
			view.append('<td><a href="{}">{}</a></td>'.format(det_link,str(x[0])))
		view.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[1]))))))
		view.append('<td>{}</td>'.format(str(x[2])))
		view.append('<td>{}</td>'.format(str(x[3])))
		view.append('<td>{}</td>'.format(str(x[4])))
		view.append('<td>{}</td>'.format(str(x[5][:56])))
		view.append('<td>{}</td>'.format(str(x[8])))
		view.append('<td>{}</td>'.format(str(x[9])))
		view.append('<td>{}</td>'.format(str(x[10])))
		view.append('<td>{}</td>'.format(x_open))
		view.append('</tr>\n')
		i = i+1

	replot = []
	
	replot.append('<h2>Bismuth Ledger Query Tool</h2>\n')
	replot.append('<p>Get a List of Transactions</p>\n')
	replot.append('<form method="post" action="/ledgerquery">\n')
	replot.append('<table>\n')
	replot.append('<tr><th><label for="block">Enter a Block number, txid, hash, address or a: followed by alias</label></th><td><input type="text" id="block" name="block" value="{}" size="68"/></td></tr>\n'.format(r_block))
	replot.append('<tr><th><label for="extra">Speed up older txid queries with a from Address (optional)</label></th><td><input type="text" id="extra" name="extra" size="68"/></td></tr>\n')
	replot.append('<tr><th><label for="sdate">Start Date (optional)</label></th><td><input type="date" id="sdate" name="sdate" value="{}" size="68"/> 00:00:00 hrs</td></tr>\n'.format(xdate))
	replot.append('<tr><th><label for="fdate">End Date (optional)</label></th><td><input type="date" id="fdate" name="fdate" value="{}" size="68"/> 23:59:59 hrs</td></tr>\n'.format(ydate))
	replot.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
	replot.append('</table>\n')
	replot.append('</form>\n')
	replot.append('<p>Note: all queries are case sensitive</p>\n')
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
	replot.append('<td><b>Operation</b></td>\n')
	replot.append('<td><b>Message Starts</b></td>\n')
	replot.append('</tr>\n')
	replot = replot + view
	replot.append('</table>\n')
	
	starter = "" + str(''.join(replot))
	
	return render_template('base.html', starter=starter)


@app.route('/sponsorinfo')
def sponsorinfo():
	
	initial = []

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
	
	starter = "" + str(''.join(initial))
	
	return render_template('base.html', starter=starter)

	#starter = "" + str(''.join(initial))

	#return starter.encode("utf-8")

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
		

	lister = []
	
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

	starter = "" + str(''.join(lister))
	
	return render_template('base.html', starter=starter)

	#html = "" + str(''.join(lister))

	#return html.encode("utf-8")

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
	
	lister = []
	
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

	starter = "" + str(''.join(lister))
	
	return render_template('base.html', starter=starter)

	
@app.route('/apihelp')
def apihelp():

	if mydisplay == 0:
		a_text = " "
	else:
		a_text = " ({} record limit)".format(str(mydisplay))
	
	return render_template('apihelp.html', atext=a_text)
	
@app.route('/details')
def detailinfo():

	try:
		getdetail = request.args.get('mydetail')
	except:
		getdetail = None
	try:
		get_addy = request.args.get('myaddress')
	except:
		get_addy = None
		
	#print(getdetail)

	if getdetail:
	
		m_detail = get_the_details(getdetail,get_addy)
	
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
			d_operation = str(m_detail[10][:30])
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
			d_operation = ""
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
		d_operation = ""
		d_open = ""
	
	return render_template('detail.html', ablock=d_block, atime=d_time, afrom=d_from, ato=d_to, aamount=d_amount, asig=d_sig, atxid=d_txid, apub=d_pub, ahash=d_hash, afee=d_fee, areward=d_reward, aoperation=d_operation, aopen=d_open)

	
@app.route('/realmem')
def realmem():
	
	return render_template('client-JustLog.html')


@app.route('/api/<param1>/<param2>', methods=['GET'])
def handler(param1, param2):

	if param1 == "stats":
		if param2 == "circulation":
			x = circ_val
			return json.dumps({'circulation':str(x)}), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

		elif param2 == "latestblock":
			x = latest()
			y = "%.2f" % x[1]
			z = str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(x[4]))))
			d = {'found':z,'height':str(x[0]),'age':str(y),'difficulty':str(x[2]),'finder':str(x[3]),'blockhash':str(x[5]),'txid':str(x[7]),'nonce':str(x[6])}
			return json.dumps(d), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			r = "invalid request"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
	elif param1 == "address":
		temp_addy = str(param2)
		if "a:" in temp_addy:
			getaddress = rev_alias(temp_addy)
		else:
			getaddress = temp_addy
		if s_test(getaddress):
			myxtions = refresh(getaddress,1)
			if float(myxtions[4]) > 0:
				x = {'address':getaddress,'alias':myxtions[8],'credits':myxtions[0],'debits':myxtions[1],'rewards':myxtions[2],'fees':myxtions[3],'balance':myxtions[4]}
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
		a_display = False
		if "f:" in getaddress:
			a_display = True
			getaddress = getaddress.split(":")[1]
			#print(getaddress)
			#print(a_display)
			
		if "a:" in getaddress:
			getaddress = rev_alias(getaddress)
			
		if not getaddress or not s_test(getaddress):
			r = "invalid data entered"
			e = {"error":r}
			return json.dumps(e), 400, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
		else:
			all = []
			conn = sqlite3.connect(bis_root)
			c = conn.cursor()
			if mydisplay == 0 or a_display:
				c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY abs(block_height) DESC;", (getaddress,getaddress))
			else:
				c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY abs(block_height) DESC LIMIT ?;", (getaddress,getaddress,str(mydisplay)))
			all = c.fetchall()
			c.close()
			conn.close()
			if not all:
				r = "address does not exist or invalid address"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				#y.append({"address":getaddress,"limit":"{} records".format(str(mydisplay))})
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"txid":str(b[5][:56]),"fee":str(b[8]),"reward":str(b[9]),"operation":str(b[10]),"openfield":str(b[11])})
				
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
			c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY abs(block_height) DESC LIMIT ?;", (getaddress,getaddress,mylimit))
			all = c.fetchall()
			c.close()
			conn.close()
			if not all:
				r = "address does not exist or invalid address"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
			else:
				y = []
				#y.append({"address":getaddress,"limit":"{} records".format(mylimit)})
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"txid":str(b[5][:56]),"fee":str(b[8]),"reward":str(b[9]),"operation":str(b[10]),"openfield":str(b[11])})
				
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
				
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"txid":str(b[5][:56]),"fee":str(b[8]),"reward":str(b[9]),"operation":str(b[10]),"openfield":str(b[11])})
				
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
								
				for b in all:
					y.append({"block":str(b[0]),"timestamp":str(b[1]),"from":str(b[2]),"to":str(b[3]),"amount":str(b[4]),"txid":str(b[5][:56]),"hash":str(b[7]),"fee":str(b[8]),"reward":str(b[9]),"operation":str(b[10]),"openfield":str(b[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

	elif param1 == "txid":
			gettxid = str(param2)
			
			gettxid = gettxid.replace(".","/")
		
			m_stuff = "{}".format(str(gettxid))
			
			m_detail = get_the_details(m_stuff,None)
	
			
			if m_detail:
			
				y = []
				y.append({"block":str(m_detail[0]),"timestamp":str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(m_detail[1])))),"from":str(m_detail[2]),"to":str(m_detail[3]),"amount":str(m_detail[4]),"signature":str(m_detail[5]),"txid":str(m_detail[5][:56]),"pubkey":str(m_detail[6]),"hash":str(m_detail[7]),"fee":str(m_detail[8]),"reward":str(m_detail[9]),"operation":str(m_detail[10]),"openfield":str(m_detail[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
			else:
				
				r = "txid does not appear to exist or invalid data"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
	elif param1 == "txidadd":
			gettxid = str(param2)
		
			tx_add_info = gettxid.split("=")
			get_txid = tx_add_info[0]
			get_add_from = tx_add_info[1]
						
			get_txid = get_txid.replace(".","/")
		
			m_stuff = "{}".format(str(get_txid))
			
			m_detail = get_the_details(m_stuff,get_add_from)
				
			if m_detail:
			
				y = []
				y.append({"block":str(m_detail[0]),"timestamp":str(time.strftime("%Y/%m/%d,%H:%M:%S", time.gmtime(float(m_detail[1])))),"from":str(m_detail[2]),"to":str(m_detail[3]),"amount":str(m_detail[4]),"signature":str(m_detail[5]),"txid":str(m_detail[5][:56]),"pubkey":str(m_detail[6]),"hash":str(m_detail[7]),"fee":str(m_detail[8]),"reward":str(m_detail[9]),"operation":str(m_detail[10]),"openfield":str(m_detail[11])})
				
				return json.dumps(y), 200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
			else:
				
				r = "txid does not appear to exist or invalid data"
				e = {"error":r}
				return json.dumps(e), 404, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
				
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
		#getaddress = str(param2)
		temp_addy = str(param2)
		if "a:" in temp_addy:
			getaddress = rev_alias(temp_addy)
		else:
			getaddress = temp_addy
		if s_test(getaddress):
			m_info = bgetvars(getaddress)
			#print(m_info)
			if m_info:
				x = {'address':str(m_info[0]),'alias':str(m_info[5]),'latestblock':str(m_info[1]),'firstblock':str(m_info[2]),'totalblocks':str(m_info[3]),'rewards':str(m_info[4])}
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
				y = []
				d_result = list(reversed(d_result))
				
				for v in d_result:
					b = str(v[0])
					d = (b,v[1])
					y.append(d)
		
		else:
			dog = False
		
		c.close()
		conn.close()

		if dog:
			#y = [b,d]
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
	'/time_chart', 'Blocktime',
	'/details', 'Details'
)

application = tornado.web.Application([
    (r'/', WSHandler),
])

if __name__ == "__main__":

	background_thread = threading.Thread(target=buildtoolsdb)
	background_thread.daemon = True
	background_thread.start()
	app_log.info("Databases: Start Thread")
	
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(8080)
	whttp_server = tornado.httpserver.HTTPServer(application)
	whttp_server.listen(wport)
	IOLoop.instance().start()
	
	#app.run()
