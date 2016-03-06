# Dynamic-Graph-Visualization

------------------------------------------------------------------------------------------------------------------
We develop a general framework using Gephi's Graph Streaming API (https://gephi.org/) to visualize a large dynamic network 
which is presented in a rapid stream of edges. 
We consider two popular dynamic networks: paper citation network and Twitter retweet network, 
and feed their edge streams into Gephi's visualization pool through a low-level programming communication with Gephi's Graph Streaming API. 
Also, we make those dynamic graphs capable of displaying a few prominent nodes which may be considered as important components, 
i.e., nodes with in-degrees/out-degrees beyond certain threshold values.

This project may help researchers visualize the implicit structures of most popular timeevolving networks 
and facilitate the development of algorithms for finding interesting subgraph patterns in them.
