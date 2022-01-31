# Report: Two Flags Agent

Daniel Yakovlev, Daniel Greenhut

## 1. Representation and Data Structures

a. We represented each board by two bitboards(padded bt zeros), one for each player's pawns.
for visualizing the game we used application packages to handle widget window, 
and the chess-python library to represent each pawn as svg figure. See [the GameBoard class](../Board.py).

![white bitboard](white_bitboard.png)
![black bitboard](black_bitboard.png)
![board](visualization.png)


b. The agent keeps a graph - implemented by hash table - where each node consists
*only the bitboards*, and the final ply is updated also in the visualizing board.
The evaluation of each node is computed only once and then saved in the node.
See [The graph and best agent classes](../Agents.py).
The best agent also use a depth scheduler and additional thread as a permanent brain.


c. The algorithm generates its moves using the lists of all possible legal moves,
which are computed by bitwise operations. See ```legal_moves``` method of [FBoard](../Board.py).
We perform an alpha-beta search where the branches of each node are
the legal moves of the corresponding board state. 

d. The algorithm detects terminal moves using the ```is_checkmate``` method of [FBoard](../Board.py)
which checks all possible ways to win.

e. In order to allocate time per move we schedule the search depth before each ply:

- First 2 moves are initialized with a small depth that is proportional to the
- game time according to our measures.
- We than add/substract constants from the searching depth, by thresholding the ratio
between the last move and time left to play. in that way we reach high depths
for advanced states in the game and yet prevent too slow searches.
- In any case, we will not search deeper than 20 plys forward.
See ```depth_scheduler``` method of [BestAgent](../Agent.py).

f. Our Agent keep revealing new nodes in the graph when the opponent is thinking. This search is 
performed in such a way that it can be stopped as soon as the opponent makes his move.
See ```keepSearch``` method of [BestAgent](../Agent.py).

## 2. Heuristic Function

a-c. We designed a static evaluation function as following:
- the evaluation of winning is 5000 and of losing is -5000, and it is completely symmetric.
- we define an "attacker" as a pawn which is able to reach the final row (and win) for sure.
we determine if such a pawn exists by checking that the bitmap in front of him, on his column and 
the two columns next to him are clear(false). here is an example of an attacker and a non-attacker
(the black pawn):

![attacker](attacker.png)
![non-attacker](nonattacker.png)

- We first check for opponent attackers of distance smaller than 5. if such exists, the node 
heuristic shall be -1000 * (5 - distance from the final row). Otherwise, we check if an attacker
of our own exists, and evaluate it in the same way.
- In case there are no attackers, we try to evaluate a state (and its brunch) by the number of 
possible moves, both of our agent and of the opponent. We use a threshold to determine the maximal 
number of possible moves that is worth evaluating. We take under concern also the case in which both 
players have a small number of possible moves.
  - Otherwise, we evaluate the heuristic by the ratio :```(my_pawns - opp_pawns) / opp_pawns```.

d. Recall that the features are normalized in such a way that winning is 5000 for each type of winning.
Note that our heuristic at each node corresponds a specific way to win, so the pruning is much more effective.

e. [-5,000, 5,000]

f. Recall a.

g. We designed several heuristics and made tournaments to test the best ways of evaluation.
We also played against other agents (of other teams) and used our mistakes as a feedback.

h. In the following section some xomplicated boards situations will be represented among the heuristic the white agent evaluates from the current board.

![expample1](heuristic1.png)

heuristic is -2000

![expample1](heuristic2.png)

heuristic is 3000

![expample1](heuristic3.png)

If white turn then heuristic is 3000, otherwise it is -3000

i. The heuristic is used for leaves as well as for the pruning of alpha-beta.

## 3. Search Algorithm

a. The search algorithm is alpha-beta pruning with depth scheduler as described above.

b. We did, as mentioned at the above section.

c. The graph described earlier contains all possible transpositions as described earlier, and
new transpositions are calculated using the bitmaps(above). 

d. The depth is in the range [2, 20] and the mean depth is in the range [7, 12] 
(varies for different opponents.)

e. The game branching factor is approximately 8.

f. According to our observations the effective branching factor is 1.7. example:

![evbf](ebf.png)

## 5. General Questions

a. at the beginning of the development process we got to explore a lot about representing
chess boards, designing agents in terms of code and building the project structure in general.
We chose to write our code strongly object-oriented. However, we had to make a lot of changes
even before starting developing the heuristic.

For example, we first implemented each board representation as a string (fen) and we discovered 
that the time of a single search is unacceptably high.

At the beginning. where most of the work included technical issues we divided the work between both
of us, but when we started designing the actual agent, we spent long nights together on zoom.

b.
- It is impossible to save on a laptop all possible states of the two flags game
- Although it is much simpler than chess, it is very hard to represent.
- A good heuristic for the game is at all not trivial.

c. It is important to choose a language that best fits the problem. In that case we first chose python
for learning algorithms, but eventually we believe that for efficiency it is better to work with C/C++
to implement an agent like that.

d. We highly recommend dividing the project into sub-missions during the semester.    

The source code and installation explanations can be found in the [README](../README.md)

[Linux executable](https://drive.google.com/file/d/1jovYaGXtJ-t1b8nJucoKT8gqWz0Pr03B/view)
to run on ```localhost 9999```.

Looking at the console of the executable, you will notice that we are starting to count moves from
-2. That is because the agent is starting with a warmup of 3 random moves. Therefore, We count the
fourth move as the first one.

Here is an example of a short game where our agent
wins another, simpler one (The agent is Black)

![1](game1.png)

![2](game2.png)

![3](game3.png)

![4](game4.png)

![5](game5.png)

![6](game6.png)

![7](game7.png)

![8](game8.png)

![9](game9.png)

![10](game10.png)

![11](game11.png)

![12](game12.png)

![13](game13.png)

![14](game14.png)

![15](game15.png)

![16](game16.png)

![17](game17.png)

another example, where the agent is black

![1](1.png)

![2](2.png)

![3](3.png)

![4](4.png)

![5](5.png)

![6](6.png)

![7](7.png)

![8](8.png)

![9](9.png)

![10](10.png)

