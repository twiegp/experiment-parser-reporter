### hyperinflation.py meta

## Required vars

# ID (str): This is the id of the experimental session of this observation.
# Pool_Label (str): This is an extra label meant to group different sessions. For example, if some sessions were from lab subjects and some were from a demo, given them different labels in order to compare data between these two groups.
# Order (int): This is the round number or order in which the results should be shown in the slides.
# Banned Intervals (list): 

meta = {"1_1.csv": {						"ID": "1_1",
											"Pool_Label": "Demo",
											"Order": 1,
											"Banned_Intervals": []
										},
		"2_1.csv": {						"ID": "2_1",
											"Pool_Label": "Run",
											"Order": 1,
											"Banned_Intervals": []
										},
		"1_2.csv": {						"ID": 	"1_2",
											"Pool_Label": "Demo",
											"Order": 2,
											"Banned_Intervals": []
										},
		"2_2.csv": {						"ID": "2_2",
											"Pool_Label": "Run",
											"Order": 2,
											"Banned_Intervals": []
										},
		"1_3.csv": {						"ID": 	"1_3",
											"Pool_Label": "Demo",
											"Order": 3,
											"Banned_Intervals": []
										},
		"2_3.csv": {						"ID": "2_3",
											"Pool_Label": "Run",
											"Order": 3,
											"Banned_Intervals": []
										}
		}