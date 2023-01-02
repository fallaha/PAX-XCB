from adb import adb_commands
from adb import sign_m2crypto
import stat
import sys
import os
import time
import json

tty = sys.argv[1]
port = 'COM{},115200'.format(tty)
command = sys.argv[2]

def init_device(addr):
	device = adb_commands.AdbCommands()
	device.ConnectDevice(port_path=None, serial=addr)
	#device.ConnectDevice(port_path=None, serial="192.168.43.168:5555")
	#device.ConnectDevice(port_path=None, serial="/dev/ttyS4,115200")
	return device

def scandir(path, device):
	files = [] 
	directories = []
	unknowns = []
	result = device.List(path)
	for i in result[2:]:
		if stat.S_ISDIR(i[1]):
			directories.append(i[0])
		if stat.S_ISREG(i[1]) and ((i[1] & stat.S_IRUSR) or (i[1] & stat.S_IRGRP) or (i[1] & stat.S_IROTH)):
			files.append(i[0])
		else:
			unknowns.append(i[0])
	return files, directories, unknowns

def tree(path, device):
	exclude = ["proc", "sys", "dev"]
	all_files = []
	all_directories = []
	all_unknowns = []
	queue = []
	current = path
	while True:
		files, directories, unknowns = scandir(current, device)
		for file in files:
			all_files.append(current + file.decode('utf-8'))
		for directory in directories:
			all_directories.append(current + directory.decode('utf-8') + '/')
			if directory.decode('utf-8') not in exclude:
				queue.append(current + directory.decode('utf-8') + '/')
		if not queue:
			break
		current = queue.pop()
		#print(current)

	return all_files, all_directories, all_unknowns

device = init_device(port)
if sys.argv[2] == 'ls':
	root = device.List(sys.argv[3])

	for i in root:
		print(i[0].decode('utf-8') + ' Perm: ' + str(oct(i[1])) + ' Size: ' + str(i[2]))

if command == 'pull':
	if sys.argv[4]:
		target = sys.argv[4]
	else:
		target = sys.argv[3].replace('/', '_')
	root = device.Pull(sys.argv[3], target)
	print(root)

if command == 'push':
	root = device.Push(sys.argv[3], sys.argv[4])
	print(root)

if command == 'logcat':
	logcat = device.Logcat()
	print(logcat)

if command == 'forward':
	print("For port forwarding (ie: for gdbserver) use the original XCB client. xcb.exe connect com:COM12; xcb.exe forward tcp:2020 tcp:2020")
	print("The protocol for port forwarding should be ADB compatible. However python-adb doesn't support it as of now")

if command == 'dump':
	name = sys.argv[3]
	print("[+] Listing everything")
	all_files, all_directories, all_unknowns = tree('/', device)
	print("[+] Creating local structure")
	target = "dumps/" + name + '/'
	if not os.path.isdir(target):
		os.mkdir(target)
	for dir in all_directories:
		if not os.path.isdir(target + dir):
			os.mkdir(target + dir)
	print("[+] Pulling all files")
	for file in all_files:
		if not os.path.isfile(target + file):
			time.sleep(1)
			try:
				device.Pull(file, target + file)
				print("[+] Downloading " + file)
			except:
				print("[-] Failed downloading " + file)
				os.remove(target + file)
				# This sucks but...
				device = None
				time.sleep(5)
				device = init_device(port)
	print("[+] Saving lists")
	with open(target + 'files.txt', 'w') as f:
		f.write(json.dumps(all_files))
	with open(target + 'directories.txt', 'w') as f:
		f.write(json.dumps(all_directories))
	with open(target + 'unknowns.txt', 'w') as f:
		f.write(json.dumps(all_unknowns))
	
