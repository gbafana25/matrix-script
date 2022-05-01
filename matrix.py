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
	return (j['access_token'], j['device_id'])



def logout(key):
	s = requests.post("https://matrix.org/_matrix/client/v3/logout?access_token="+key);


# takes entered text and formats it as json for http request
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
	c = input("Which room? (or (q)uit)> ")
	try:
		if(int(c) > count):
			print("Room index out of range, exiting...")
			exit(0)
	# will exit of any non-numeric key is pressed
	except ValueError:
		exit(0)
	return rms[int(c)]
	




def get_joined_rooms(key): 
	r = requests.get(BASE_URL+"/joined_rooms?access_token="+key)
	resp = json.loads(r.text)
	return resp['joined_rooms']
	

# format room aliases as url-compatible, not used right now
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


# not used now
def get_aliases(u):
	aliases = {}
	for j in range(len(u)):
		inp = input("Enter alias: ")
		s = requests.get(BASE_URL+"/directory/room/"+urlstr(inp))
		p = json.loads(s.text)
		for i in range(len(u)):
			if(p['room_id'] == u[i]):
				aliases[u[i]] = inp 
			

	return aliases



def get_messages_since(b, key):
	req = requests.get(BASE_URL+"/sync?since="+b+"&access_token="+key)
	p = json.loads(req.text)
	return p
	

def sync_from_room(key, batch, rms, data):	
	room = select_room(rms)
	print("----------------------"+ Style.BRIGHT + Fore.GREEN + room + Style.RESET_ALL + "--------------------------")
	try:
		for s in data['rooms']['join'][room]['timeline']['events']:
			try:
				print(Fore.RED + s['sender'] + Style.RESET_ALL, ":", s['content']['body'])
			except:
				pass
	except KeyError:
		print("No new messages")
	d = input("(t)ype message or (q)uit (any other key to go back)> ")
	if(d == "q"):
		print("Exiting...")
		exit(0)
	elif(d == "t"):
		n = input("> ")
		send = requests.put(BASE_URL+"/rooms/"+room+"/send/m.room.message/"+str(randint(1,92392))+"?access_token="+key, data=fmtmsg(n))
		sync_from_room(key, batch, rms, data)
	else:
		sync_from_room(key, batch, rms, data)




# gets batch number (points to certain time)
def get_batch(key):
	req = requests.get(BASE_URL+"/sync?access_token="+key)
	p = json.loads(req.text)
	return p['next_batch']




# dumps all room messages at once
def sync_and_read_all(key, rms):
	req = requests.get(BASE_URL+"/sync?access_token="+key)
	p = json.loads(req.text)
	for room in rms:	
		print("---------------------"+ Style.BRIGHT + Fore.GREEN + room + Style.RESET_ALL +"---------------------------")
		for s in p['rooms']['join'][room]['timeline']['events']:
			try:
				print(Fore.RED + s['sender'] + Style.RESET_ALL, ":", s['content']['body'])
			except:
				pass
		print("------------------------------------------------------")


	

def setup():
	print("Logging in...")
	k = login()
	rew = open("config.json", "w")
	j = get_joined_rooms(k[0])
	print("Getting rooms...")
	print("Updating aliases...")
	batch = get_batch(k[0])
	print("Getting most recent batch number...")
	new_data = {
		"api_key":k[0],
		"device_id":k[1],
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


def print_help():
	print("-------------Available Commands--------------------")
	print()
	print("setup - login and generate config file")
	print("unread - get unread messages")
	print("read_all - get all messages at once (since batch #)")
	print("refresh_rooms - refresh list of joined rooms")
	print("logout")
	print()
	print("---------------------------------------------------")

		


if len(sys.argv) != 2:
	print_help()
elif sys.argv[1] == "setup":
	setup()
elif sys.argv[1] == "unread":
	tup = get_config()
	m = get_messages_since(tup[1], tup[0])
	sync_from_room(tup[0], tup[1], tup[2], m)
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
	print_help()
	

