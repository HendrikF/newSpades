

def getCommands(parent):
	def stop(self, args):
		self.stopNow = True
		print("Stopping server...")
	parent.addCommand(stop, "stop", "Shuts the server down. No arguments.")
	
	def help(self, args):
		if len(args) == 0:
			str = "Aviable commands: "
			for x in self.commands.keys():
				str += x+" "
			print(str)
		else:
			if args[0] in self.help.keys():
				if self.help[args[0]] is None:
					print("No help aviable!")
				else:
					print(self.help[args[0]])
			else:
				print("Command does not exist!")
	parent.addCommand(help, "help", "Shows all commands or help for single command.\nUsage: help [commandname]")
	
	def master(self, args):
		self.config["master"] = not self.config["master"]
		print("Master broadcast toggled "+ ("ON" if self.config["master"] else "OFF")+"!")
	parent.addCommand(master, "master", "Switches master broadcast ON/OFF. No arguments.")
	
	def show_players(self, args):
		print("Currently", self.numberOfPlayers, "players online.")
	parent.addCommand(show_players, "list", "Shows number of players online. No arguments.")

def getHooks(Hooks):
	class ScriptHooks(Hooks):
		def hook_Start(self):
			#print("Hello!")
			Hooks.hook_Start(self)
		
		def hook_Run(self):
			Hooks.hook_Run(self)
		
		def hook_Stop(self):
			#print("Goodbye!")
			Hooks.hook_Stop(self)
	return ScriptHooks
	
	
	
	