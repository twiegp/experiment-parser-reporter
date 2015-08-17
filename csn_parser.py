# Standard python libraries
import sys, os
from copy import deepcopy
from operator import itemgetter

# Dataset object for a particular experiment.
class dataset:
	def __init__(self, cli_args):
		self.exp_name = cli_args[0]
		self.exp_path = cli_args[1]
		self.output_path = cli_args[2]
		self.debug = int(cli_args[3])
		
		m = __import__(self.exp_name)
		self.exp_class = getattr(m, self.exp_name)
		
	# Read in metadata concerning the experiment.	
	def read_meta(self):
		sys.path.append(self.exp_path)
		self.exp_metadata = __import__("exp_meta").meta
	
	# For each item in the metadata file, run the session corresponding to that item.
	def run_all(self):
		print "Running "+str(len(self.exp_metadata.keys()))+" sessions"
		for k,v in self.exp_metadata.iteritems():
			self.run(k,v)
			
	# Run a single session.
	def run(self, filename, session_metadata):
	
		# Set up a new object of the experiment class
		print "Session "+session_metadata["ID"]
		exp_particular = deepcopy(self.exp_class(self.debug))
		
		# Open the raw file and have the experiment convert it to instructions for running the simulation.
		with open(self.exp_path + "/" + filename) as raw:
			raw_lines = raw.readlines()
		
			# Format the raw lines into nice csv strings.
			formatted_lines = [exp_particular.line_formatter(line) for line in raw_lines]
			formatted_lines = [line.strip() for line in formatted_lines if line != None] # Remove blank lines.
			
			# Convert those csv strings into instruction dictionaries.
			instructions = [exp_particular.parse_line(line) for line in formatted_lines]
			instructions = [instruction for instruction in instructions if instruction != None] # Remove blank messages.
			
			# Initialize the session object. First pull out the parameter lines, then pass them to the initialization method along with the metadata.
			paramlines = [instruction for instruction in instructions if instruction["Instruction"] == "Parameter"]
			exp_particular.initialize(paramlines, session_metadata)
			
			# Set up the output file, then get the headers from the session object and write them to a blank .csv.
			with open(self.output_path+"/"+session_metadata["ID"]+".csv","wt") as output:
				exp_headers = exp_particular.headers
				output.write(",".join(exp_headers)+"\n")
				
				# Get the start and stop times of the experiment.
				start_time, stop_time = exp_particular.get_times(instructions)
				
				# Determine intervals that won't be processed
				banned_times = []
				try:
					banned_intervals = session_metadata["Banned_Intervals"]
					for pair in banned_intervals:
						banned_times += range(int(pair[0]),int(pair[1])+1)
				except KeyError: # No banned list present.
					pass
				
				# For each second in that time range, get the event messages for that time and then update the model.
				ticks = 0
				for n in range(stop_time - start_time):
					this_time = start_time + n
					
					if this_time in banned_times:
						continue
						
					ticks += 1
					print "running "+str(this_time)
					
					# Get the event messages for this time and sort them if there's millisecond-level data.
					eventlines = [instruction for instruction in instructions if instruction["Instruction"] == "Event" and int(float(instruction["When"])) == this_time]
					eventlines.sort(key=itemgetter("When"))
					
					# Process each event
					for event in eventlines:
						exp_particular.process_event(event)
					
					# Now get the state of the experiment and write it to the .csv file.
					row = exp_particular.get_state(this_time,ticks)
					output.write(",".join([str(v) for v in row.values()])+"\n")
					
					# Tell the experiment that a second has passed in order to update any relevant variables.
					exp_particular.update()
		
data = dataset(sys.argv[1:5])
data.read_meta()
data.run_all()