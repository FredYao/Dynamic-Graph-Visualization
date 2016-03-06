'''
Created on Nov 14, 2013

@author: yibo

Instructions:

In order to run this script, make sure Tweepy has been installed as a site-package of your Python.
Use this script with Gephi and its Graph Streaming plugin.
1. Apply for consumer key and secret, and access token and secret from Twitter's Developers 'https://dev.twitter.com/';
2. Fill out the corresponding keys and secrets at the beginning of this script;
3. Make sure the module GephiJsonClient.py is in the same directory of this script;
4. Open Gephi and create a new project;
5. Go to the tab "Streaming", right-click on "Master Server", and then click on "Start";
6. Go to the tab Layout, select "Force Atlas" and click "Run";
7. Specify the hashtags (or topics) that you want to track at the beginning of this script, please refer to 'http://tweitgeist.colinsurprenant.com/' for top hashtags on Twitter;
8. Run this script.
'''


####################################################################
# Set the keys and tokens used to access the Twitter Streaming API

consumer_key="";
consumer_secret="";
access_token="";
access_token_secret="";

####################################################################

# the topics (hashtags) need to be specified, multiple topics (hashtags) are allowed
HASH_TAGS = ['#BELIEVEMOVIE'];


#===============================================================================
# Import modules
#===============================================================================
import re;
from collections import deque;
from tweepy import StreamListener;
from tweepy import OAuthHandler;
from tweepy import Stream;
from GephiJsonClient import GephiJsonClient;
import Tkinter;
import thread;


#===============================================================================
# Global variables and functions
#===============================================================================
NODE_ATTRIBUTE = {"size":10, 'r':125.0/255, 'g':125.0/255, 'b':125.0/255};
INTRO_INFO = '''This application shows Twitter's global stream of Retweet data in a dynamic fashion.
Nodes are representing users on Twitter while edges representing retweet information.
If a user i retweets another user j's tweet, there is a directed edge pointing from node i to node j.''';
                
IN_THRESHOLD = 10;  # threshold value for setting in-degree
OUT_THRESHOLD = 10; # threshold value for setting out-degree

def setSize( degree):
    '''
    Set size of a node according to its degree.
    '''
    if degree >= 50:
        return 30;
    elif degree >= 30:
        return 25;
    elif degree >= 10:
        return 20;


#===============================================================================
# Class definition
#===============================================================================
class RetweetStream(StreamListener):
    '''
    A class which inherits from tweepy.StreamListener.
    It's a listener that handles retweet data received from the stream.
    '''  
    
    def __init__(self, url="http://localhost:8080/workspace0", on_gui = True):
        StreamListener.__init__(self);
        self.url = url;
        self.g = GephiJsonClient(url = self.url);
        self.g.cleanAll();  
        self.degree_dict = {};
        self.retweeted_dict = {};
        self.displayed_users = deque(maxlen=1000);
        self.displayed_dict = {};
        self.current_tm = "";
        
                      
    def on_status(self, status):
        '''
        Receive retweet streams from Twitter's streaming API.
        Fetch the original user who has the tweet and the users who retweet this tweet.
        '''
        # find the RETWEET pattern
        m = re.search('(?<=RT\s@)\w+', status.text);
        if m is not None:
            source_user = m.group(0).lower();   # the user who writes the tweet
            from_user = status.author.screen_name.lower();  # the user who retweets the tweet
            date = status.created_at;
            print status.id,":", from_user,"--->", source_user;
            
            # update the retweeted list of the source_user
            self.retweeted_dict[source_user] = self.retweeted_dict.get(source_user, []);
            self.retweeted_dict[source_user].append(from_user);
            
            # update degrees
            if self.degree_dict.get(source_user) == None:
                self.degree_dict[source_user] = [1,0]; # [indegree, outdegree]
            else:
                self.degree_dict[source_user][0] += 1;
            if self.degree_dict.get(from_user) == None:
                self.degree_dict[from_user] = [0,1];
            else:
                self.degree_dict[from_user][1] += 1;
            
            # add fromnode to Gephi's visualization pool
            if self.displayed_dict.get(from_user) == None:
                self.displayed_dict[from_user] = from_user;
                if len(self.displayed_users) >= self.displayed_users.maxlen:
                    deletenode = self.displayed_users.popleft();
                    del self.displayed_dict[deletenode];
                    self.g.deleteNode(deletenode);
                node_attributes = NODE_ATTRIBUTE.copy();
                node_attributes['label'] = from_user;
                self.g.addNode(from_user, **node_attributes);
                self.displayed_users.append(from_user);
            
            # check fromnode's out-degree, and update it in Gephis' pool
            if self.degree_dict[from_user][1] >= OUT_THRESHOLD:
                sz = setSize(self.degree_dict[from_user][1]);
                node_attributes = NODE_ATTRIBUTE.copy();
                node_attributes['r'] = 0.0/255;
                node_attributes['g'] = 200.0/255;
                node_attributes['b'] = 0.0/255;
                node_attributes['size'] = sz;
                self.g.changeNode(from_user, **node_attributes);

               
            # check tonode's out-degree, and update it in Gephi's pool
            if self.displayed_dict.get(source_user) == None:
                self.displayed_dict[source_user] = source_user;
                if len(self.displayed_users) >= self.displayed_users.maxlen:
                    deletenode = self.displayed_users.popleft();
                    del self.displayed_dict[deletenode];
                    self.g.deleteNode(deletenode);
                node_attributes = NODE_ATTRIBUTE.copy();
                node_attributes['label'] = source_user;
                self.g.addNode(source_user, **node_attributes);
                self.displayed_users.append(source_user);
            
            else:
                if self.degree_dict[source_user][0] >= IN_THRESHOLD and self.degree_dict[source_user][1] >= OUT_THRESHOLD:
                    sz = setSize(self.degree_dict[source_user][0]);
                    node_attributes = NODE_ATTRIBUTE.copy();
                    node_attributes['r'] = 0.0/255;
                    node_attributes['g'] = 0.0/255;
                    node_attributes['b'] = 100.0/255;
                    node_attributes['size'] = sz;
                    self.g.changeNode(source_user, **node_attributes);
                elif self.degree_dict[source_user][0] >= IN_THRESHOLD:
                    sz = setSize(self.degree_dict[source_user][0]);
                    node_attributes = NODE_ATTRIBUTE.copy();
                    node_attributes['r'] = 0.0/255;
                    node_attributes['g'] = 200.0/255;
                    node_attributes['b'] = 0.0/255;
                    node_attributes['size'] = sz;
                    self.g.changeNode(source_user, **node_attributes);
                
            attributes = {'directed':True, 'weight':2.0, 'date':str(date)}
            self.g.addEdge(status.id, from_user, source_user, **attributes)
       
            
    def clear_data(self):
        '''
        Clear up.
        '''
        if self.g is not None:
            self.g.cleanAll();
        del self.degree_dict;
        del self.displayed_users;
        del self.known_users;

        

#===============================================================================
# Class definition
#===============================================================================
class GUI(Tkinter.Tk):
    '''
	GUI of the application.
    '''
    
    def __init__(self):
        Tkinter.Tk.__init__(self);
        self.title("Dynamic Retweet Network (Twitter)");
        self.is_run = True;
        self.initializeUI();
        
    
    def initializeUI(self):
        '''
		Initialize the GUI.
        '''
        
        # part 1
        self.intro_lf = Tkinter.LabelFrame(self, text="INTRODUCTION", height=500, width=150);
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
        legnd_cvs.create_oval(15,22,30,37,fill="gray"); legnd_cvs.create_text(40,22,text="ordinary user",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,42,30,57,fill="green"); legnd_cvs.create_text(40,42,text="user who retweets >= "+str(OUT_THRESHOLD)+" tweets",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,62,30,77,fill="blue"); legnd_cvs.create_text(40,62,text="user who has >= "+str(OUT_THRESHOLD)+" retweets and retweeted by >= "+str(IN_THRESHOLD)+" users",anchor=Tkinter.NW);
        legnd_cvs.create_oval(15,82,30,97,fill="red"); legnd_cvs.create_text(40,82,text="user retweeted by >= "+str(IN_THRESHOLD)+" users",anchor=Tkinter.NW);
        legnd_cvs.create_text(10,112,anchor=Tkinter.NW, text="Node Size:");
        legnd_cvs.create_text(15, 132, text="large:", anchor=Tkinter.NW); legnd_cvs.create_text(75,132,text="in-degree(out-degree) >= 50", anchor=Tkinter.NW);
        legnd_cvs.create_text(15, 152, text="medium:", anchor=Tkinter.NW); legnd_cvs.create_text(75,152,text="in-degree(out-degree) >= 30", anchor=Tkinter.NW);
        legnd_cvs.create_text(15, 172, text="small:", anchor=Tkinter.NW); legnd_cvs.create_text(75,172,text="in-degree(out-degree) >= 10", anchor=Tkinter.NW);
        space_lbl_1 = Tkinter.Label(self, text="");
        space_lbl_1.pack(fill=Tkinter.BOTH, expand=1);
        
        #part 3
        self.date_lf = Tkinter.LabelFrame(self, text="CURRENT INQURY HASHTAGS", height=50, width=150);
        self.date_lf.pack(fill=Tkinter.BOTH, expand=1);
        self.date_txt = Tkinter.StringVar();
        date_lbl = Tkinter.Label(self.date_lf, text=','.join(HASH_TAGS), padx=10);
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

    
    def run(self):
        auth = OAuthHandler(consumer_key, consumer_secret);
        auth.set_access_token(access_token, access_token_secret);
        self.listener = RetweetStream();
        streamer = Stream(auth, self.listener, timeout=30);
        streamer.filter(track=HASH_TAGS);
        
        
    def pressStart(self):
        '''
        Function triggered by clicking 'START' button.
        It will start a new thread to simulate the streaming fashion.
        '''
        thread.start_new(self.run, ());
        self.start_btn['state'] = Tkinter.DISABLED;
    
    
    def pressQuit(self):
        '''
        Function triggered by clicking 'QUIT' button.
        It will stop running application and quit it.
        '''
        self.is_run = False;
        self.quit();
#===============================================================================
# TEST
#===============================================================================
# TEST
if __name__ == '__main__':
#    auth = OAuthHandler(consumer_key, consumer_secret);
#    auth.set_access_token(access_token, access_token_secret);
#    l = RetweetStream();
#    streamer = Stream(auth, l, timeout=30);
#    streamer.filter(track=['#RIPNELSONMANDELA','#MTVSTARS']);
    a = GUI();
    a.mainloop();

      
        
