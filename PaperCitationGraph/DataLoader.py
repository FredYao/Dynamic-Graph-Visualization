'''
Created on Nov 20, 2013

@author: yibo

Class DataLoader.
'''


#===============================================================================
# Class definition
#===============================================================================
class DataLoader(object):
    '''
    The class is responsible for reading data from a file which contains a set of edge streams.
    Each line of the file is formatted as: 'node1','node2','timestamp'.
    '''
    
    def __init__(self):
        self.fobj = None;       # a file object
        self.timestamp = [];    # a lost for storing timestamps
        self.edge_stream = {};  # key: a time point, value: a list of edges streamed in
        self.counter = 0;

  
    def loadData(self, filename):
        '''
        Load edge streams from a data file.
        '''
        print "Loading data from file ", filename;
        self.fobj = open(filename, "r");
        for eachline in self.fobj:
            [fromid, toid, date] = eachline.strip().split(",");
            if len(self.timestamp) == 0:
                self.timestamp.append(date);
            elif self.timestamp[-1] != date:
                self.timestamp.append(date);
            
            self.edge_stream[date] = self.edge_stream.get(date, []);
            self.edge_stream[date].append((fromid, toid, ));
        print "Complete loading!\n\n"; 
        self.fobj.close();
        
        
    def flush(self):
        '''
        Reset the counter to 0.
        '''
        self.counter = 0;   

    
    def sendData(self):
        '''
        Send the nodes and edges of each timestamp.
        '''
        if self.counter < len(self.timestamp):
            tm = self.timestamp[self.counter];
            edge_set = self.edge_stream[tm];
            #print "Batch #", self.counter+1, "(",tm,"), new edges: ", len(edge_set);
            self.counter += 1;
        else:
            tm = -1;
            edge_set = None;

        return tm, edge_set;


    def clearData(self):
        '''
        Clean up all the data structures.
        '''
        del self.edge_stream; 
        del self.timestamp; 
        self.flush();


        
    
