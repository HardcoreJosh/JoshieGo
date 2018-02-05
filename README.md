# JoshieGo
A Go playing program implemented in Tensorflow roughly according to the architecture of AlphaGo. 
JoshieGo has strong policy/value network, and uses APV-MCTS to search during live play. On a single GTX1080 given 20 seconds per move, 
JoshieGo achieve strength around 5~6 amateur dan on OGS and Tencent's Foxy Go Server.


## What is special about JoshieGo?
Compared to many other AlphaGo related but failed projects, JoshieGo does not aim to faithfully replicate AlphaGo's original paper, especially in the training
of value network which is crucial for final performance. Rather, JoshieGo aims to build practical and strong 
Go engine with acceptable time and affordable hardware. 
The value network of JoshieGo is trained and fine-tuned purely with publicly available data using
supervised learning without obvious overfitting. In fact, the author of JoshieGo does not believe the original AlphaGo paper can be replicated 
by ordinary person due to the expansive self-play data generation stage for training value network. Policy network and APV-MCTS are implemented 
as described in AlphaGo paper, with the exception that we do not use a fast roll-out policy.

## How to play

### Requiments

Tensorflow >= 1.0.0

Numpy >= 1.11.1

OpenCV (optional, visualization use only)

### Start a Game

1. Edit IP Address in play.py

2. run python play.py --is_server=1

3. run python play.py

## Selected games by JoshieGo

1. https://online-go.com/game/11545426. A win against RoyalZero(5d Go program on OGS). 
2. https://online-go.com/game/11529651. A win against Nicaso(2d Go program on OGS).

More games can be found by searching username "JoshieBot" on Tencent's Foxy Go Server.

## Futher work

1. Surprisingly, JoshieGo can not read ladder. Feature planes indicating successful ladder capture and ladder escape will be added.
2. Wrap feature extraction code in C to boost performance.
3. Implement distributed APV-MCTS.
