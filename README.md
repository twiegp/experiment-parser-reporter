# Experimental Data Report Generator

This pipeline is meant to provide a standard structure for accomplishing the following tasks using experimental data:

- Use raw event logs from experimental sessions to run an internal simulation of the underlying experiment and provide sanity checks for the raw logs - does each event message seem to reflect a valid action taken within the experiment?
- Create a flat file reflecting the state of the internal simulation at each second of its existence.
- Take the set of flat files and use them to generate a beamer report conveying key information about some variables of interest.

This pipeline includes data from one experiment, called "hyperinflation", that can be worked through the entire process by running the steps outlined in the **master.R** file. This documentation will walk through each step in this process, from building a Python script that simulates your data to an R script that generates objects for your report.

Internally, I've also built pipelines for four additional experiments that I've run during my time at the Center for the Study of Neuroeconomics. It is meant to to be flexible enough that new experiments should be able to be input into this framework in a relatively-straightforward fashion.

Note that this assumes that the appropriate R libraries are installed, as well as Python 2.7 and MiKTeX.

## Step 1: Organize Raw Data

All of the raw data files should be placed in a subdirectory. In the hyperinflation case this raw directory is called "workingData". In addition to these raw files, a file called **exp_meta.py** must exist in this directory.

**exp_meta.py** should define a simple object called "meta", which is a dictionary where each key is a name of one of the raw files that will be read and each value is a dictionary with a set of additional metadata about that file in particular. Here's a shortened version of the **exp_meta.py** file used for hyperinflation:

```python
meta = 	{"1_1.csv": {						
											"ID": "1_1",
											"Pool_Label": "Demo",
											"Order": 1,
											"Banned_Intervals": []
											}
		}
```

This will end up instructing the parser to read the file **1_1.csv**, which contains some raw data, as well as assign some additional pieces of information to each row of its flat file. Some of this information is essential to the functionality of the parser - check out **exp_meta.py** for additional details on the meaning of each key.

Note that at this time three assumptions about these raw data files need to hold for them to be amenable to this pipeline:

1. Each line in the raw file should correspond to at most one event.
2. Each event in the raw file should correspond to exactly one line.
3. Each event should have a timestamp somewhere in its line.

## Step 2: Generate a Parser

Each experiment must have a parser defined that will translate its raw event files into a set of flat .csv files. The main parser file is **csn_parser.py**, which takes a command-line argument to import an experiment-specific module that defines how parsing and model simulation should occur. For the hyperinflation example, this experiment-specific module is found in **hyperinflation.py**, and the parser can be run through the following command-line argument:

```
csn_parser.py hyperinflation workingData results
```

This will run **csn_parser.py**, with the first argument specifying that the experiment module being used will be found in **hyperinflation.py**, the second argument specifying that the raw data (along with **exp_meta.py**) can be found in the "workingData" directory, the third argument specifying that the flat files will be put into the "results" directory.

Each experiment module will need to contain the following methods:

- *line_formatter()*: Formats a raw line into some specific csv format for parsing. The main goal here is to reconcile different raw files which may have different string formats and to output a common csv format.
- *parse_line()*: Takes these formatted lines and converts them into dictionaries depending on their meaning. Each dictionary needs to have an *Instruction* key, whose values specify whether the line corresponds to an event ("Event") or some information that will be used to initialize the simulation ("Parameter"). Dictionaries that are specified as events must also have a "When" key corresponding to the timestamp when this event occurred.
- *initialize()*: This sets up the experiment simulation using the defined parameter lines as well as the metadata.
- *get_state()*: Queries each object in the experiment simulation for its state variables. These will be output to the flat file for the given session, along with some additional information.
- *get_times()*: This tells the main **csn_parser.py** script when the experiment actually begins and ends depending on the event and parameter dictionaries. Only events that are between this start time and stop time (and not in one of the banned intervals defined in **exp_meta.py**) will be processed.
- *process_event()*: Translates an event dictionary generated from *parse_line()* into an update of the objects in the experiment simulation, and optionally performs sanity checks to make sure that the updates seem reasonable.
- *update()*: Once all the events timestamped with a given second are processed, this will perform and second-by-second updates of the experimental objects that are necessary.

```python
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
```

In the hyperinflation example, there are two sorts of simulation objects: Players and a Market. Each player is initialized to have some inventory, and as raw events are processed by the parser these player objects are updated. For example, when a "Contract" event occurs this means that some in our experiment player traded a unit of some good for a unit of another good with a different player. We use information from this event message to update the player objects, as well as make sure that this event constituted a legal move within the experiment: For example, if Player 3 traded 1 unit of Good 1 for 1 unit of Good 2 from Player 2, we make sure that Player 3 actually had 1 unit of Good 1 when this event occurred - otherwise, we might have some problem with our experiment.

As the parser runs this simulation, it is also dumping data about the state of the simulation out as our flat data in the results folder. The data contained in the "results" directory contains the flat parsed data that is the output of running the 6 files defined in **exp_meta.py** through the parser.

## Step 3: Configure master.R

The entire pipeline for this process should be controllable through the **master.R** file. Setting up for a new experiment should be a simple matter of redefining the options defined at the beginning of this script to the appropriate variables.

```r
### Generic options for any experiment.
options(
  experiment = "hyperinflation",
  working_path = "YOUR WORKING PATH HERE",
  python_prefix = "python", # If the shell needs a command-line prefix to run a Python script, put it here.
  raw_folder = "workingData",
  output_folder = "Results",
  filenames = c("1_1.csv","1_2.csv","1_3.csv","2_1.csv","2_2.csv","2_3.csv"), # These are the results files to be read into the dataset.
  group_labels = c("Demo","Run"), # These are the pool labels whose data will be seperately modeled
  comparison_labels = NA, # This is the label where comparison data will be derived from, if applicable.
  comparison_treatments = NA, # These are the treatment conditions from the comparison data that will be used, if applicable.
  comparison_file = NA # If this exists in the working directory, this file will be loaded and appended on as containing preprocessed comparison data.
)

### Particular options for this experiment.
options(
)
```

The above code shows the option definitions for the hyperinflation experiment. The *comparison* options are for allowing pre-parsed data to be quickly imported and merged onto newly-parsed data, so that generating a new report does not mean reparsing every single raw file (which can take a long time.) This functionality is not currently being used in the hyperinflation example.

```r
source("pipeline.R")

parse_raw() # First, take any raw data that needs to be processed and do so.
read_parsed() # Read processed raw data in.
format_parsed()  # Format the processed raw data.
merge_parsed() # Take the formatted data and merge it with already-processed data, if necessary.
generate_objects() # Take formatted data and generate objects from it for the report.
generate_report() # Generate the report.
```

These 6 functions, defined in **pipeline.R**, control the 6 steps of the report generation procedure. The first function, *parse_raw()*, calls the python parsing script described in Step 2. *read_parsed()* then reads in the flat .csv files generated by the parser and merges them all into a single data frame. For new experiments, updating **pipeline.R** will be necessary to direct it to load additional necessary files - for example, steps in these sequence rely on calling functions called *format()* and *make_objects()*, and these functions are defined in a file called **hyperinflation_formatter.R**. This file is opened within **pipeline.R**. For a new experiment, a new file containing these functions should be made and **pipeline.R** should be directed to open these files when *format_parsed()* and *generate_objects()* is called.

## Step 4: Define format() in R

The purpose of the *format()* function is to generate additional derived variables that do not reflect the minimal state variables of the simulation objects in the parser. 

```r
format <- function(df.full) {
  # Not much formatting necessary for now!!
  df.full$Milk <- recode(df.full$Market_Price_Last_1,"-1=NA")
  df.full$Eggs<- recode(df.full$Market_Price_Last_2,"-1=NA")
  df.full$Sugar <- recode(df.full$Market_Price_Last_3,"-1=NA")
  
  assign("df_formatted", df.full, envir = .GlobalEnv) # Assign back for saving, if necessary.
}
```

In the above example, all that is done is that new derived variables are created that just relabel the prices of each market (from 1 to 3) as "Milk", "Eggs", and "Sugar", which will come in handy when labeling the visualizations, as these were the actual goods traded in the experiment. It is also necessary that this function assigns an object called *df_formatted* back to the global environment, as this will be the input to the *merge_parsed()* function that is called next by the pipeline.

## Step 5: Define make_objects() in R

*make_objectes()* takes the fully-formatted (and merged) data frame and now creates the specific objects that are necessary for the beamer report. For the hyperinflation experiment, this involves generating a graph for the price of each of the three goods (milk, eggs, and sugar) over each of the six rounds defined in **exp_meta.py**, as well as outputting some info about these rounds into **pipelineFiles/slideInfo.csv**.

```
Label,Order,Plotname,Exchanged_1,Exchanged_2,Exchanged_3,Supply_1,Supply_2,Supply_3
Demo,1,Prices_1_1,66,63,51,119,103,84
Run,1,Prices_2_1,69,59,52,108,106,90
Demo,2,Prices_1_2,77,62,65,129,101,100
Run,2,Prices_2_2,63,62,48,112,110,99
Demo,3,Prices_1_3,70,62,57,112,97,94
Run,3,Prices_2_3,66,64,50,110,138,109
```

In general, this step will either save objects to the global R environment so that they can be included in the R markdown file that generates the report, or to some file such as **slideInfo.csv** that will be used to generate the R markdown file. More on this in the next step.

## Step 6: Create the R markdown file that will generate the report

The *generate_report()* function at the end of **master.R** loads an R markdown template and attempts to fill it in using the objects in the global environment. The name of this template is again defined in **pipeline.R** and will need to be modified for new experiments, but for hyperinflation the template name that is called is **hyperinflation_template_filled.Rmd**.

Note that depending on the structure of the report, this file might need to be dynamically generated. For example, the hyperinflation report has one slide per round, but what if the number of rounds were 4 or 8 rather than 6? In this instance, a python script should be defined that takes a template .Rmd file (in the hyperinflation case, **hyperinflation_template.Rmd**) and uses relevant data to format a new template made for the data being used. In the hyperinflation case, this file is **hyperinflation_template_formatter.py** and it uses the information contained in **pipelineFiles/slideInfo.csv** to generate **hyperinflation_template_filled.Rmd**, which is then rendered by R to include the price plots for each round that were saved to the global space in the *make_objects()* function. This gives the final output report - **hyperinflation.pdf**.
