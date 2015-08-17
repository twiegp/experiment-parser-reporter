# Converts text into final csv format as necessary
import time

def test(yes,*args): # Takes a list - first val is the test, second is the msg that gets printed if the list fails
	if yes:
		for test in args:
			if test[0] != 1:
				print test[1]
				raw_input()
				
class Market:

	def __init__(self):
		self.transacted = {"1": 0, "2": 0, "3": 0}
		self.last_prices = {"1": -1, "2": -1, "3": -1} # This will be recoded to NAs in R, presumably.
		
	def report(self):
		reportDict = {}
		for k,v in self.transacted.iteritems():
			reportDict.update({ "Market_Transactions_"+k : v})	
		for k,v in self.last_prices.iteritems():
			reportDict.update({ "Market_Price_Last_"+k : v})	
		return reportDict

class Player:

	def __init__(self, num, item_1, item_2, item_3, money):
	
		# Init vars
		self.num = num
		self.inv = {"1": item_1, "2": item_2, "3": item_3, "Money": money}
		
		# Fixed params not given through param lines.
		
		# State-tracking variables
		
		# Derived state-tracking variables that convey event information.
		self.harvested = {"1": item_1, "2": item_2, "3": item_3}
		
	def roundEnd(self):
		pass
		
	def checkStatus(self, debug, item_1, item_2, item_3, money, eventDict):
		test(
				debug, 
				[int(item_1) == self.inv["1"], "Item 1, Player " + str(self.num) + " Inventory Error :" + str(eventDict)],
				[int(item_2) == self.inv["2"], "Item 2, Player " + str(self.num) + " Inventory Error :" + str(eventDict)],
				[int(item_3) == self.inv["3"], "Item 3, Player " + str(self.num) + " Inventory Error :" + str(eventDict)],
				[int(money) == self.inv["Money"], "Money, Player " + str(self.num) + " Inventory Error :" + str(eventDict)]
			)
	
	# After every second, do this.
	def updateTime(self):
		pass
		
	# Send values back for reporting
	def report(self):
		reportDict = {}
		
		# Append relevant init vars
		reportDict.update({	"Subject_"+str(self.num)+"_Num" : self.num})
		for k,v in self.inv.iteritems():
			reportDict.update({ "Subject_"+str(self.num)+"_Item_"+k : v})
		
		# Append relevant state-tracking vars
		
		# Append event-tracking vars
		for k,v in self.harvested.iteritems():
			reportDict.update({ "Subject_"+str(self.num)+"_Harvested_"+k : v})
		
		return reportDict

class hyperinflation:  

	def __init__(self, debug):
		self.debug = debug
		self.round = 1
		
	# Formats a raw line into some specific csv format for parsing. In this case we just want to remove the "X" at the beginning of each line.
	def line_formatter(self, line):
		lineSplit = line.split(",")[1:] # Take off recorder timestamp
		if len(lineSplit) < 2:
			return None
		ts = lineSplit[1]
		ts = str(time.mktime(time.strptime(ts,"%Y-%m-%dT%H:%M:%S.%f0Z")))
		lineSplit = [ts] + lineSplit
			
		return ",".join(lineSplit).strip()
		
	# Takes each line and converts it into either a parameter or some sort of instruction for the model.
	def parse_line(self, line):
		#print line
		lineSplit = line.split(",")
		when = lineSplit[0]
		when_raw = lineSplit[2]
		type = lineSplit[3]
		
		if type == "START":
			return {	"Instruction": "Parameter", "Type": "Params", "When": when, "When Raw": when_raw,
						"Players": lineSplit[5], 
						"Item 1 Start": lineSplit[8], "Item 2 Start": lineSplit[9], "Item 3 Start": lineSplit[10], "Money Start": lineSplit[11]}
					
		elif type == "INVENTORY":
			return {	"Instruction": "Event", "Type": "Inventory", "When": when, "When Raw": when_raw,
						"Inventory": [{"1": lineSplit[5*n + 4], "2": lineSplit[5*n + 5], "3": lineSplit[5*n + 6], "Money": lineSplit[5*n + 7], "Utility": lineSplit[5*n + 8]} for n in range((len(lineSplit)-4)/5)]}
				
		elif type == "HARVEST":
			return { 	"Instruction": "Event", "Type": "Harvest", "When": when, "When Raw": when_raw,
						"Who": lineSplit[4], "Item Type": lineSplit[5]}
						
		elif type == "CONTRACT":
			return { 	"Instruction": "Event", "Type": "Contract", "When": when, "When Raw": when_raw,
						"Item Type": lineSplit[4], "Price": lineSplit[5], "Buyer": lineSplit[6], "Seller": lineSplit[7]}
						
		elif type == "Reset":
			pass
			
		elif type == "END":
			return {	"Instruction": "Event", "Type": "Stop", "When": when,  "When Raw": when_raw}
						
		else:
			raw_input("Event not recognized: " + line)
			
			
		# For all other lines.
		return None
				

	# Initalize the objects in the model using the metadata and all parameter lines from the raw file.
	def initialize(self, paramlines, metadata):
		
		# Save metadata for later referencing
		self.metadata = metadata
		
		# First, get number of players and starting inventory.
		self.playerNum = int([dict["Players"] for dict in paramlines if dict["Type"] == "Params"][0])
		item1init = int([dict["Item 1 Start"] for dict in paramlines if dict["Type"] == "Params"][0])
		item2init = int([dict["Item 2 Start"] for dict in paramlines if dict["Type"] == "Params"][0])
		item3init = int([dict["Item 3 Start"] for dict in paramlines if dict["Type"] == "Params"][0])
		moneyinit = int([dict["Money Start"] for dict in paramlines if dict["Type"] == "Params"][0])
		
		# Assumes that treatments can always be read from certain lines.
		
		# Initialize objects
		self.playerList = [Player(num = n, item_1 = item1init, item_2 = item2init, item_3 = item3init, money = moneyinit) for n in range(self.playerNum+1)]
		self.market = Market()
		
		# Make headers for variables that will be sent back. Do this by getting the dictionaries of the states of each player object, then only looking at the keys.
		self.headers = self.get_state().keys()
		
	# Get the state of each object that has data to report.
	def get_state(self, time = 0, tick = -1):
		reportDict = {	"ID" : self.metadata["ID"],
						"Players_N" : self.playerNum, "Pool_Label": self.metadata["Pool_Label"], "Order": self.metadata["Order"],
						"Time": time, "Tick": tick}
		for player in self.playerList:
			reportDict.update(player.report())
		reportDict.update(self.market.report())
		return reportDict
		
	# Get the start and stop time for the session so the main script knows when to start and stop processing events.
	def get_times(self, instructions):
		startTime = int(float([instruction["When"] for instruction in instructions if (instruction["Type"] == "Params")][0])) # If multiple messages exist, get the first one.
		stopTime = int(float([instruction["When"] for instruction in instructions if instruction["Type"] == "Stop"][0]))
		return startTime, stopTime
		
	# Turn an event dictionary into an update of the objects being modeled.
	def process_event(self,event):
		type = event["Type"]
		
		if type == "Harvest":
			index = int(event["Who"])
			type = event["Item Type"].strip()
			self.playerList[index].inv[type] += 1
			self.playerList[index].harvested[type] += 1
		
		elif type == "Contract":
			buyer_index = int(event["Buyer"])
			seller_index = int(event["Seller"])
			type = event["Item Type"].strip()
			price = int(event["Price"])
			
			
			self.playerList[buyer_index].inv[type] += 1
			self.playerList[seller_index].inv[type] -= 1
			
			if buyer_index != 0:
				test([self.playerList[buyer_index].inv["Money"] >= price, "Error: Bought without enough money: " + str(event)])
				self.playerList[buyer_index].inv["Money"] -= price
			if seller_index != 0:
				self.playerList[seller_index].inv["Money"] += price
			
			self.market.transacted[type] += 1
			self.market.last_prices[type] = price
			
		elif type == "Inventory":
			inventory_list = event["Inventory"]
			for n, dict in enumerate(inventory_list):
				thisPlayer = self.playerList[n]
				thisPlayer.checkStatus(self.debug, dict["1"], dict["2"], dict["3"], dict["Money"], event)
			
		# Don't care about other messages!
		else:
			pass
	
	# Perform any operations on the state before moving to the next time period, if necessary. In this case that means giving them 
	def update(self): 
		pass