# Experimental Data Report Generator

This pipeline is meant to provide a standard structure for accomplishing the following tasks using experimental data:

- Use raw event logs from experimental sessions to run an internal simulation of the underlying experiment and provide sanity checks for the raw logs - does each event message seem to reflect a valid action taken within the experiment?
- Create a flat file reflecting the state of the internal simulation at each second of its existence.
- Take the set of flat files and use them to generate a beamer report conveying key information about some variables of interest.

This pipeline includes data from one experiment, called "hyperinflation", that can be worked through the entire process by running the steps outlined in the **master_parser.R** file. This documentation will walk through each step in this process, from building a Python script that simulates your data to an R script that generates objects for your report.

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

In the hyperinflation example, there are two sorts of simulation objects: Players and a Market. Each player is initialized to have some inventory, and as raw events are processed by the parser these player objects are updated. For example, when a "Contract" event occurs this means that some in our experiment player traded a unit of some good for a unit of another good with a different player. We use information from this event message to update the player objects, as well as make sure that this event constituted a legal move within the experiment: For example, if Player 3 traded 1 unit of Good 1 for 1 unit of Good 2 from Player 2, we make sure that Player 3 actually had 1 unit of Good 1 when this event occurred - otherwise, we might have some problem with our experiment.

As the parser runs this simulation, it is also dumping data about the state of the simulation out as our flat data in the results folder. The data contained in the "results" directory contains the flat parsed data that is the output of running the 6 files defined in **exp_meta.py** through the parser.
