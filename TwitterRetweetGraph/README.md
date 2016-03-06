On Twitter, a retweet is a re-posting of someone else's tweet to make it shared with the public. Among the huge volume of tweets generated per second on Twitter, a large part of them are retweets. In this project, we focus on the retweets regarding certain given topics (or hashtags) in Twitter's public streams. By accessing Twitter's Streaming API through Tweepy, we are able to retrieve all retweets with respect to certain specified topics (or hashtags) from the real-time public streams. Each retweet has the author who did the re-posting and the user who wrote the original tweet, which can imply a retweet-relation between the author and the original user. So in the retweet network, the nodes are used to represent the users on Twitter with the usernames being the unique identifiers. And the edges are used to denote retweet-relations between them. If a user i re-posted another user j's tweet, there will be a directed edge pointing from node i to node j in the retweet network.


---------------------------------------
Instructions for how to run the scripts.


Install Gephi and the Streaming Plugin

1. Download the proper version of Gephi from https://gephi.org/users/download/
2. Install Gephi on your machine
3. Open Gephi, go to the menu 'Tools' and select 'Plugins'
4. Go to the tab 'Available Plugins', select 'Graph Streaming' and click 'Install'
5. Restart Gephi, check if there is a 'Streaming' tab on the left panel 


Install Tweepy

1. Go to https://github.com/tweepy/tweepy to download Tweepy and install it (Please refer to README file in Tweepy for instructions about installation)
2. Open a Python IDE and a Python interactive window, type 'import tweepy' to check if it installed successfully


Retweet Network

1. Go to Twitter's Developers https://dev.twitter.com/ and apply for consumer key and secret, and access token and secret
2. Make sure the modules GephiJsonClient.py and RetweetStream.py are in the same directory
3. Open Gephi and create a new project
4. Go to the tab "Layout", select "Force Atlas" and click "Run"
5. Open "RetweetStream.py", change the hashtags (or topics) that you want to track (a Python list named 'HASH_TAGS'), and fill out the consumer key and secret, and the access token and secret
6. Run the script "RetweetStream.py"
