import sys, os

templateName = "hyperinflation_template.Rmd"
outputName = "hyperinflation_template_filled.Rmd"
csvPath = "pipelineFiles/slideInfo.csv" # The code for the tables will be here.
#fontsize = "tiny"

template = open(templateName,"r").read()
info = open(csvPath).readlines()[1:] # Throw out first line

orderDict = {} # NYI. Translate order into a plaintext interpretation? (eg. Round 1 is no government, round 2 is limited government, etc.)

# Take lines and make them into a list of dicts, one dict per slide.
infoList = [{	"Label" : line.split(",")[0], "Order" : line.split(",")[1], "Plotname" : line.split(",")[2], 
				"E_Milk" : line.split(",")[3], "E_Eggs": line.split(",")[4], "E_Sugar" : line.split(",")[5], 
				"S_Milk" : line.split(",")[6], "S_Eggs": line.split(",")[7], "S_Sugar" : line.split(",")[8]} for line in info]

inputStringFull = ""
	
for d in infoList:
	inputStringLocal = "## Market Prices (Round %s Group %s) ## \n Milk Exchanged: %s, Eggs Exchanged: %s, Sugar Exchanged: %s \n Milk Supply: %s, Eggs Supply: %s, Sugar Supply: %s\n\n" % (d["Order"], d["Label"], d["E_Milk"], d["E_Eggs"], d["E_Sugar"], d["S_Milk"], d["S_Eggs"], d["S_Sugar"])
	inputStringLocal += "```{r, echo=F, warning=F}\nplot(" + d["Plotname"] +")\n```\n\n"
	
	inputStringFull += inputStringLocal
	
template = template % (inputStringFull)
open(outputName,"wt").write(template)


