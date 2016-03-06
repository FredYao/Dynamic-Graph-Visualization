The paper citation dataset considered in this project is Arxiv HEPTH (high energy physics theory),
which was originally released in 2003 KDD Cup, and was later refined into XML-based representation. 
Each paper is denoted by a node with a unique identifier in the graph, and if a paper i cites another paper j, 
there is a directed edge pointing from node i to node j. 
The dataset contains papers submitted to Arxiv in the period from January 1993 to April 2003.
In order to make the citation data flow into Gephi's workspace in a real-time fashion, 
we have converted the XML-based data into a set of edge streams and then store them in a plain text file (http://www.eecs.wsu.edu/~yyao/DirectedStudyII/Data/Citation_Stream).


--------------------------------------------------------------------------------------------------------------------------

Instructions for how to run the scripts.


---------------------------------------
Install Gephi and the Streaming Plugin

1. Download the proper version of Gephi from https://gephi.org/users/download/
2. Install Gephi on your machine
3. Open Gephi, go to the menu 'Tools' and select 'Plugins'
4. Go to the tab 'Available Plugins', select 'Graph Streaming' and click 'Install'
5. Restart Gephi, check if there is a 'Streaming' tab on the left panel 



----------------
Citation Network

1. Make sure the modules DataLoader.py, GephiJsonClient.py and CitationStream.py, and the data file Citation_Stream are in the same directory
2. Open Gephi and create a new project
3. Go to the tab "Streaming", right-click on "Master Server", and then click on "Start"
4. Go to the tab "Layout", select "Force Atlas" and click "Run"
5. Run the script "CitationStream.py"
