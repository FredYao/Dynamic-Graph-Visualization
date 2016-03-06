'''
Created on Oct 9, 2013

@author: yibo

Instructions:

Use this script with Gephi and its Graph Streaming plugin.
1. Make sure the modules DataLoader.py and GephiJsonClient.py, and the data file Citation_Stream are in the same directory of this script;
2. Open Gephi and create a new project;
3. Go to the tab "Streaming", right-click on "Master Server", and then click on "Start";
4. Go to the tab Layout, select "Force Atlas" and click "Run";
5. Run this script.
'''


#===============================================================================
# Import modules
#===============================================================================
import time;
from DataLoader import DataLoader;
from GephiJsonClient import GephiJsonClient;
from collections import deque;
import Tkinter;
import thread;


#===============================================================================
# Global variables and functions
#===============================================================================
NODE_ATTRIBUTE = {"size":10, 'r':125.0/255, 'g':125.0/255, 'b':125.0/255};
INTRO_INFO = '''This application shows a Citation Network in a dynamic fashion. 
The dataset was released in 2003 KDD Cup competition. 
Nodes are representing papers while edges representing citation information. 
If a paper i cites a paper j, there is a directed edge pointing from node i to node j.  
The dataset contains papers published in Jan 1992 till Dec 2000. 
The papers are streaming into the visualization pool in a Daily time unit.''';
                
IN_THRESHOLD = 20;  # threshold value for setting in-degree
OUT_THRESHOLD = 40; # threshold value for setting out-degree
BATCH_SPEED = 0.1;   # time for sleeping between each two batches


def setSize( degree):
    '''
    Set size of a node according to its degree.
    '''
    if degree >= 100:
        return 30;
    elif degree >= 50:
        return 25;
    elif degree >= 20:
        return 20;

    
    
#===============================================================================
# Class definition
#===============================================================================
class CitationStream(Tkinter.Tk):
    '''
    This class is responsible for sending citation edge streams (loaded by using DataLoader)
    to Gephi's Master server by using GephiJsonClient.
    '''
    
    def __init__(self, url = 'http://localhost:8080/workspace0', filename='Citation_Stream', on_gui = True):
        self.url = url;
        self.filename = filename;
        self.loader = DataLoader();     # create an instance of DataLoader
        self.loader.loadData(self.filename);    # load data from file
        self.g = GephiJsonClient(url=self.url);     # create an instance of GephiJsonClient
        self.g.cleanAll();
        self.degree_dict = {};
        self.cited_dict = {};
        
        # elemts for GUI
        self.is_run = True;
        self.is_gui = on_gui;
        if self.is_gui == True:
            self.initializeUI();
    
    
    def run(self):
        self.loader.flush();
        self.g.cleanAll();
        self.degree_dict.clear();
        self.cited_dict.clear();
        self.streamIn(IN_THRESHOLD , OUT_THRESHOLD, BATCH_SPEED);
        
    
    def runForever(self):
        i = 1;
        while self.is_run:
            print "ROUND #", i;
            self.run();
            print "Waiting 10 seconds for the next round...";
            if self.is_gui == True:
                self.date_txt.set("Waiting 10 seconds for the next round...");
                
            time.sleep(10);  
            i += 1;
  
              
    def streamIn(self, in_threshold = 10, out_threshold = 30, timeout=1):
        '''
        Feed fetch batch into Gephi's pool.
        The maximum number of nodes displayed in the pool is set to be 1000.
        The nodes with in-degree >= in_threshold or out-degree >= out_threshold 
        will be highlighted using different colors and sizes. 
        timeout will be the time for sleeping between two batches.
        '''
        displayed_nodes = deque(maxlen=1000);    # create a queue and set its size 1000. There are 1000 nodes will be displayed in Gephi's pool
        displayed_dict = {};    # store nodes which are currently existing in Gephi's pool
        
        while True:
            tm,edgeset = self.loader.sendData();
            if tm == -1 or edgeset == None:
                break;
            
            print "Batch: ", tm;
            if self.is_gui == True:
                self.date_txt.set(tm);
                
            for fromnode,tonode in edgeset:
                # update the cited list of the tonode
                self.cited_dict[tonode] = self.cited_dict.get(tonode,[]);
                self.cited_dict[tonode].append(fromnode);
                
                # update degrees
                if self.degree_dict.get(fromnode) == None:
                    self.degree_dict[fromnode] = [0,1, tm];  # [in-degree, out-degree, date]
                else:
                    self.degree_dict[fromnode][1] += 1;
                if self.degree_dict.get(tonode) == None:
                    self.degree_dict[tonode] = [1,0, tm];    # [in-degree, out-degree, date]
                else:
                    self.degree_dict[tonode][0] += 1;
                
                # add the fromnode to Gephi's pool
                node_attributes = NODE_ATTRIBUTE.copy();
                if displayed_dict.get(fromnode) == None:
                    displayed_dict[fromnode] = fromnode;
                    # check the size
                    if len(displayed_nodes) >= displayed_nodes.maxlen:
                        deletenode = displayed_nodes.popleft();
                        del displayed_dict[deletenode];
                        self.g.deleteNode(deletenode);  # delete the node from Gephi's pool
                    self.g.addNode(fromnode, **node_attributes);
                    displayed_nodes.append(fromnode);
                    
                # check fromnode's in-degree, and update it in Gephis' pool
                if self.degree_dict[fromnode][1] >= out_threshold:
                    sz = setSize(self.degree_dict[fromnode][1]);
                    node_attributes['size'] = sz;
                    node_attributes['r'] = 0.0/255;
                    node_attributes['g'] = 200.0/255;
                    node_attributes['b'] = 0.0/255;
                    self.g.changeNode(fromnode, **node_attributes);
                    
                # check tonode's out-degree, and update it in Gephi's pool
                node_attributes = NODE_ATTRIBUTE.copy();
                if displayed_dict.get(tonode) == None:
                    if str(int(self.degree_dict[tonode][2][0:4])+5)+self.degree_dict[tonode][2][4:7] >= tm[0:7]:
                        displayed_dict[tonode] = tonode;
                        # check the size
                        if len(displayed_nodes) >= displayed_nodes.maxlen:
                            deletenode = displayed_nodes.popleft();
                            del displayed_dict[deletenode];
                            self.g.deleteNode(deletenode);
                        if self.degree_dict[tonode][0] >= in_threshold and self.degree_dict[tonode][1] >= out_threshold:
                            sz = setSize(self.degree_dict[tonode][0]);
                            node_attributes['size'] = sz;
                            node_attributes['r'] = 0.0/255;
                            node_attributes['g'] = 0.0/255;
                            node_attributes['b'] = 100.0/255;
                        elif self.degree_dict[tonode][0] >= in_threshold:
                            sz = setSize(self.degree_dict[tonode][0]);
                            node_attributes['size'] = sz;
                            node_attributes['r'] = 200.0/255;
                            node_attributes['g'] = 0.0/255;
                            node_attributes['b'] = 0.0/255;
                        self.g.addNode(tonode, **node_attributes);
                        displayed_nodes.append(tonode);
                        # connect the tonode to those nodes that cite it and already in Gephi's pool
                        for eachcit in self.cited_dict[tonode]:
                            if displayed_dict.get(eachcit) != None:
                                self.g.addEdge(str(eachcit+"->"+tonode), eachcit, tonode, directed=True);
                else:
                    if self.degree_dict[tonode][0] >= in_threshold and self.degree_dict[tonode][1] >= out_threshold:
                        sz = setSize(self.degree_dict[tonode][0]);
                        node_attributes['size'] = sz;
                        node_attributes['r'] = 0.0/255;
                        node_attributes['g'] = 0.0/255;
                        node_attributes['b'] = 100.0/255;
                    elif self.degree_dict[tonode][0] >= in_threshold:
                        sz = setSize(self.degree_dict[tonode][0]);
                        node_attributes['size'] = sz;
                        node_attributes['r'] = 200.0/255;
                        node_attributes['g'] = 0.0/255;
                        node_attributes['b'] = 0.0/255;
                    self.g.changeNode(tonode, **node_attributes);         
                self.g.addEdge(str(fromnode+"->"+tonode), fromnode, tonode, directed=True);
            
            # sleep for seconds if one timestamp is done
            time.sleep(timeout);  
        
        # clear
        displayed_nodes.clear();
        displayed_dict.clear();
         
                       
    def clearData(self):
        '''
        Clear up.
        '''
        self.loader.clearData();
        self.degree_dict.clear();
        self.cited_dict.clear();
        
    
    #----------------------
    # Functions for the UI
    #----------------------
    def initializeUI(self):
        '''
        Initialize the components needed in the UI.
        '''
        Tkinter.Tk.__init__(self);  
        self.title("Dynamic Citation Network");                
        self.date_txt = Tkinter.StringVar();
            
        # part 1
        self.intro_lf = Tkinter.LabelFrame(self, text="INTRODUCTION", height=200, width=150);
        self.intro_lf.pack(fill=Tkinter.BOTH, expand=1);
        intro_lbl = Tkinter.Label(self.intro_lf, text=INTRO_INFO, wraplength=400, justify=Tkinter.LEFT, padx=10, pady=10);
        intro_lbl.pack(side=Tkinter.LEFT, expand=1);
        space_lbl_1 = Tkinter.Label(self, text="");
        space_lbl_1.pack(fill=Tkinter.BOTH, expand=1);
        #part 2
        self.legnd_lf = Tkinter.LabelFrame(self, text="LEGEND", height=200, width=150);
        self.legnd_lf.pack(fill=Tkinter.BOTH, expand=1);
        legnd_cvs = Tkinter.Canvas(self.legnd_lf, height=200, width=150);
        legnd_cvs.pack(fill=Tkinter.BOTH, expand=1);
        legnd_cvs.create_text(10,2,anchor=Tkinter.NW, text="Node Color:");
        legnd_cvs.create_oval(15,22,30,37,fill="gray"); legnd_cvs.create_text(40,22,text="an ordinary paper",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,42,30,57,fill="green"); legnd_cvs.create_text(40,42,text="a paper cites >= "+str(OUT_THRESHOLD)+" papers",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,62,30,77,fill="blue"); legnd_cvs.create_text(40,62,text="a paper cites >= "+str(OUT_THRESHOLD)+" papers and cited by >= "+str(IN_THRESHOLD)+" papers",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,82,30,97,fill="red"); legnd_cvs.create_text(40,82,text="a paper cited by >= "+str(IN_THRESHOLD)+" papers",anchor=Tkinter.NW);
        legnd_cvs.create_text(10,112,anchor=Tkinter.NW, text="Node Size:");
        legnd_cvs.create_text(15, 132, text="large:", anchor=Tkinter.NW); legnd_cvs.create_text(75,132,text="in-degree(out-degree) >= 50", anchor=Tkinter.NW);
        legnd_cvs.create_text(15, 152, text="medium:", anchor=Tkinter.NW); legnd_cvs.create_text(75,152,text="in-degree(out-degree) >= 30", anchor=Tkinter.NW);
        legnd_cvs.create_text(15, 172, text="small:", anchor=Tkinter.NW); legnd_cvs.create_text(75,172,text="in-degree(out-degree) >= 10", anchor=Tkinter.NW);
        space_lbl_1 = Tkinter.Label(self, text="");
        space_lbl_1.pack(fill=Tkinter.BOTH, expand=1);
        
        #part 3
        self.date_lf = Tkinter.LabelFrame(self, text="CURRENT DATE", height=200, width=150);
        self.date_lf.pack(fill=Tkinter.BOTH, expand=1);
        self.date_txt = Tkinter.StringVar();
        date_lbl = Tkinter.Label(self.date_lf, textvariable=self.date_txt, padx=10);
        date_lbl.pack(side=Tkinter.LEFT);
        space_lbl_1 = Tkinter.Label(self, text="");
        space_lbl_1.pack(fill=Tkinter.BOTH, expand=1);
        #part 4
        self.btn_lf = Tkinter.LabelFrame(self, text="", height=100, width=150);
        self.btn_lf.pack(fill=Tkinter.BOTH);
        self.is_run = True;
        self.start_btn = Tkinter.Button(self.btn_lf, text="START", command = self.pressStart);
        self.start_btn.pack(side=Tkinter.LEFT);
        self.quit_btn = Tkinter.Button(self.btn_lf, text="QUIT", command = self.pressQuit);
        self.quit_btn.pack(side=Tkinter.RIGHT);
        
        
    def pressStart(self):
        '''
        Function triggered by clicking 'START' button.
        It will start a new thread to simulate the streaming fashion.
        '''
        thread.start_new(self.runForever, ());
        self.start_btn['state'] = Tkinter.DISABLED;
    
    
    def pressQuit(self):
        '''
        Function triggered by clicking 'QUIT' button.
        It will stop running application and quit it.
        '''
        self.is_run = False;
        self.quit();
            
    

        
        
        
        
#===============================================================================
# MAIN function
#===============================================================================
if __name__ == '__main__':
    cs = CitationStream(on_gui=True);
    if cs.is_gui == True:
        cs.mainloop();
        pass;
    else:
        cs.runForever();

