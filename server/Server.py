
import socket
import threading
import queue
import os.path
import json
#from Commands import *

class Server(object):
	
	def __init__(self):
		self.stopNow = False
		self.numberOfPlayers = 0;
		self.playerNames = []
		self.commands = {}
		self.help = {}
		self.hooks = Hooks
		self.config = {
			"master": False,
			"password": {
				"admin": ["replaceme"]
			},
			"scripts": [
				
			]
		}
	
	def runServer(self):
		self.getConfig()
		self.getScripts()
		self.getMap()
		self.startConsoleInput()
		self.hooks.hook_Start(self)
		while True:
			self.connectToMaster()
			self.checkInput()
			self.acceptClient()
			self.hooks.hook_Run(self)
			if self.stopServer():
				break
		self.hooks.hook_Stop(self)
		self.cleanup()

	def writeConfig(self):
		f = open("config.config", "w")
		json.dump(self.config, f)
		f.close()
	
	def getConfig(self):
		"""
		TODO:
			generate/read CONFIG file
		"""
		if not os.path.isfile("config.config"):
			self.writeConfig()
			print("New Config file created!")
			return
		f = open("config.config", "r")
		self.config = json.load(f)
		f.close()
		print("Config loaded!")

	def getMap(self):
		"""
		TODO:
			generate/read MAP
			based on configuration
		"""
		pass
	
	
	"""
	protocol_class = FeatureProtocol
	connection_class = FeatureConnection

	script_objects = []
	script_names = config.get('scripts', [])
	game_mode = config.get('game_mode', 'ctf')
	if game_mode not in ('ctf', 'tc'):
		# must be a script with this game mode
		script_names.append(game_mode)

	script_names = config.get('scripts', [])

	for script in script_names[:]:
		try:
			module = __import__('scripts.%s' % script, globals(), locals(), 
				[script])
			script_objects.append(module)
		except ImportError, e:
			print "(script '%s' not found: %r)" % (script, e)
			script_names.remove(script)

	for script in script_objects:
		protocol_class, connection_class = script.apply_script(protocol_class,
			connection_class, config)

	protocol_class.connection_class = connection_class
	"""
	
	
	def getScripts(self):
		script_objects = []
		module = __import__('Commands')
		script_objects.append(module)
		for script in self.config["scripts"]:
			try:
				module = __import__('scripts.'+script)
				script_objects.append(module)
			except:
				print("Script '"+script+"' not found!")
		
		for script in script_objects:
			self.hooks = script.getHooks(self.hooks)
			script.getCommands(self)

	def startConsoleInput(self):
		"""
		TODO:
			init thread for console input
		"""
		self.ConsoleInput = ConsoleInput()
		self.ConsoleInput.setDaemon(True)
		self.ConsoleInput.start()

	def connectToMaster(self):
		"""
		TODO:
			say the master-server that we are a public server
		"""
		pass
	
	def checkInput(self):
		"""
		TODO:
			check for commands from console or client
		"""
		com = ConsoleInput.commands.get()
		name = com.pop(0)
		if name in self.commands.keys():
			try:
				self.commands[name](self, com)
			except:
				pass
		else:
			print("Unknown command!")
		ConsoleInput.commands.task_done()
		#pass
	
	def acceptClient(self):
		"""
		TODO:
			accept new clients (thread)
			new thread for each client
				exchange data between clients
				validate each action done by client
		"""
		pass

	def stopServer(self):
		"""
		TODO:
			check a variable set by console or admin command
		"""
		return self.stopNow

	def cleanup(self):
		"""
		TODO:
			close files
			free memory
			kick clients
			and so on
			exit
		"""
		pass
	
	def addCommand(self, func, name = None, usage = None):
		"""
		TODO:
			add a command to the known commands of the server
		"""
		if name is None:
			name = func.__name__
		self.commands[name] = func
		self.help[name] = usage


"""
Hooks for scripts
"""
class Hooks(object):
	def hook_Start(self):
		print("Server started!")
	
	def hook_Run(self):
		pass
	
	def hook_Stop(self):
		print("Server stopped!")


class ClientThread(threading.Thread):
	pass


class ConsoleInput(threading.Thread):
	commands = queue.Queue()
	
	def run(self):
		while True:
			com = input().split()
			self.commands.put(com)

"""
class Commands(threading.Thread):
	
	
	def run(self):
		while True:
			self.execute(ConsoleInput.commands.get())
			ConsoleInput.commands.task_done()
	
	def execute(self, com):
		func = com.pop(0)
"""









