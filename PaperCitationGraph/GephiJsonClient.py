'''
Created on Nov 20, 2013

@author: yibo

Class GephiJsonClient.
'''


#===============================================================================
# import modules
#===============================================================================
import urllib2;
try:
    import json;
except ImportError:
    try:
        import simplejson as json;
    except:
        raise "No JSON module in your Python. Requires Python 2.6+";



#===============================================================================
# Class definition
#===============================================================================
class GephiJsonClient(object):
    '''
    The class is responsible for connecting Gephi's Master server and send JSON events
    to that server.
    It will convert each network event (including adding/deleting/changing a node, 
    and adding/deleting/changing an edge) to a JSON event. 
    '''
    
    def __init__(self, url="http://localhost:8080/workspace0"):
        self.url = url;
        self.data = "";
    
    def flush(self):
        '''
        Flush with sending data.
        '''
        if len(self.data) > 0:
            self.send(self.data);
            self.data = "";
    
    def send(self, data):
        '''
        Send data to the server.
        '''
        connection = urllib2.urlopen(self.url+"?operation=updateGraph", data);
        return connection.read();

        
    
    def addNode(self,nid,**attributes):
        '''
        Adding a single node as a JSON event.
        '''
        self.data += json.dumps({"an":{nid:attributes}}) + "\r\n";
        self.flush();
        
            
    def deleteNode(self, nid):
        '''
        Deleting a single node as JSON event.
        '''
        self.data += json.dumps({"dn":{nid:{}}}) + "\r\n";
        self.flush();
    
    
    def changeNode(self, nid, **attributes):
        '''
        Change the attributes of a node.
        '''
        self.data += json.dumps({"cn":{nid:attributes}}) + "\r\n";
        self.flush();
            
            
    def addEdge(self, eid, source, target, directed=True, **attributes):
        '''
        Adding a single edge as a JSON event.
        '''
        attributes['source'] = source;
        attributes['target'] = target;
        attributes['directed'] = directed;
        self.data += json.dumps({"ae":{eid:attributes}}) + "\r\n";
        self.flush();
    
    
    def deleteEdge(self, eid):
        '''
        Deleting a single edge as a JSON event.
        '''
        self.data += json.dumps({"de":{eid:{}}}) + "\r\n";
        self.flush();
    
    
    def changeEdge(self, eid, **attributes):
        '''
        Change the attributes of an edge.
        '''
        self.data += json.dumps({"ce":{eid:attributes}}) + "\r\n";
        self.flush();
          
            
    def cleanAll(self):
        '''
        Clean all objects (including nodes and edges) of the graph.
        '''
        self.data += json.dumps({"dn":{"filter":"ALL"}}) + "\r\n";
        self.flush();

