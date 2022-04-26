#!/usr/bin/python3

import requests
import json
import sys
from random import randint
from colorama import Fore, Style, Back

BASE_URL = "https://matrix.org/_matrix/client/r0"


def login():
	user = input("Enter username: ")
	pword = input("Enter password: ")
	d = {
		"type":"m.login.password",
		"user":user,
		"password":pword,
	}
	dj = json.dumps(d)
	req = requests.post(BASE_URL+"/login", data=dj)
	j = json.loads(req.text)
	return j['access_token']



def logout(key):
	s = requests.post("https://matrix.org/_matrix/client/v3/logout?access_token="+key);

def fmtmsg(text):
	m = {
		"body":text,
		"msgtype":"m.text"
	}
	jm = json.dumps(m)
	return jm


def select_room(rms):
	count = 0
	for r in rms:
		print(str(count) + ")", r)
		count += 1
	c = input("Which room?> ")
	if(int(c) > count):
		print("Room index out of range, exiting...")
		exit(0)
	return rms[int(c)]
	




def get_joined_rooms(key): 
	r = requests.get(BASE_URL+"/joined_rooms?access_token="+key)
	resp = json.loads(r.text)
	return resp['joined_rooms']
	

def urlstr(u):
	result = ""
	for s in u:
		if(s == "#"):
			result += "%23"
		elif(s == ":"):
			result += "%3A"
		else:
			result += s
	return result


def get_aliases(u):
	aliases = {}
	for j in range(len(u)):
		inp = input("Enter alias: ")
		s = requests.get(BASE_URL+"/directory/room/"+urlstr(inp))
		p = json.loads(s.text)
		for i in range(len(u)):
			if(p['room_id'] == u[i]):
				#print(u[i])
				aliases[u[i]] = inp 
			

	return aliases
	

def sync_from_room(key, batch, rms):
	req = requests.get(BASE_URL+"/sync?since="+batch+"&access_token="+key)
	p = json.loads(req.text)
	#print(p)
	room = select_room(rms)
	#for room in rms:	
	print("----------------------"+ Style.BRIGHT + Fore.GREEN + room + Style.RESET_ALL + "--------------------------")
	try:
		for s in p['rooms']['join'][room]['timeline']['events']:
			try:
				print(Fore.RED + s['sender'] + Style.RESET_ALL, ":", s['content']['body'])
			except:
				pass
	except KeyError:
		print("No new messages")
	d = input("Type message or (q)uit> ")
	if(d == "q"):
		print("Exiting...")
		exit(0)
	else:
		send = requests.put(BASE_URL+"/rooms/"+room+"/send/m.room.message/"+str(randint(1,92392))+"?access_token="+key, data=fmtmsg(d))
		#print(send.content)
		#print(fmtmsg(d))



def get_batch(key):
	req = requests.get(BASE_URL+"/sync?access_token="+key)
	p = json.loads(req.text)
	return p['next_batch']




def sync_and_read_all(key, aliases):
	req = requests.get(BASE_URL+"/sync?access_token="+key)
	p = json.loads(req.text)
	for room in aliases:	
		print("---------------------"+ Style.BRIGHT + Fore.GREEN + aliases[room] + Style.RESET_ALL +"---------------------------")
		for s in p['rooms']['join'][room]['timeline']['events']:
			try:
				print(Fore.RED + s['sender'] + Style.RESET_ALL, ":", s['content']['body'])
			except:
				pass
		print("------------------------------------------------------")


	

def setup():
	#conf = open("config.json", "r+")
	#c = json.loads(conf.read())
	print("Logging in...")
	key = login()
	#conf.close()
	rew = open("config.json", "w")
	j = get_joined_rooms(key)
	print("Getting rooms...")
	print("Updating aliases...")
	#al = get_aliases(j)
	batch = get_batch(key)
	print("Getting most recent batch number...")
	new_data = {
		"api_key":key,
		"snapshot":batch,
		"rooms":j
	}
	nd = json.dumps(new_data)
	rew.write(nd)
	print("Updating config file...")
	rew.close()


def get_config():
	conf = open("config.json", "r+")
	c = json.loads(conf.read())
	conf.close()
	return (c['api_key'], c['snapshot'], c['rooms'])


def refresh_rooms(key):	
	c = open("config.json", "r")
	cj = json.loads(c.read())
	cj['rooms'] = get_joined_rooms(key)
	c.close()
	f = open("config.json", "w")
	f.write(json.dumps(cj))
	f.close()
		


if sys.argv[1] == "setup":
	setup()
elif sys.argv[1] == "unread":
	tup = get_config()
	sync_from_room(tup[0], tup[1], tup[2])
elif sys.argv[1] == "read_all":
	tup = get_config()
	sync_and_read_all(tup[0], tup[2])
elif sys.argv[1] == "logout":
	tup = get_config()
	logout(tup[0])
elif sys.argv[1] == "refresh_rooms":
	tup = get_config()
	refresh_rooms(tup[0])
else:
	print("invalid command")


