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

This will end up instructing the parser to read the file "1_1.csv", which contains some raw data, as well as assign some additional pieces of information to each row of its flat file. Some of this information is essential to the functionality of the parser - check out **exp_meta.py** for additional details on the meaning of each key.

## Step 2: Generate a Parser
