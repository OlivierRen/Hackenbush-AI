# https://www.javatpoint.com/mini-max-algorithm-in-ai (contains pseudo code for minimax algo)

# Minmax at line 155
# TODO 
# - implement alpha-beta pruning
# - Currently im writing the code where the simulated_game function does all the work, 
# theres probably a way to use both functions later 
# change win/loss ratio scale based on length of game (maybe even complexity)
# Automatic level creator

from collections import defaultdict, deque
from functools import partial
from itertools import count, repeat, compress
from operator import eq
from enum import StrEnum

import matplotlib.pyplot as plt
import networkx as nx

import random


class Color(StrEnum):
    R = RED = "red"
    B = BLUE = "blue"

    @property
    def other(self):
        if self is Color.R:
            return Color.B
        else:
            return Color.R


BranchDict = dict[Color, dict[int, set[int]]]


def get_edges(branches: BranchDict):
    """get a list of edges and colors from a dictionary of branches"""
    seen = {0}
    remaining = deque(seen)

    edges = []
    colors = []

    # bfs since colors need to be specified in this order to draw correctly
    while remaining:
        curr = remaining.popleft()
        for c in Color:
            new_vertices = branches[c][curr] - seen

            seen.update(new_vertices)
            remaining.extend(new_vertices)

            edges.extend(zip(repeat(curr), new_vertices))
            colors.extend(repeat(c, len(new_vertices)))

    return edges, colors


def get_branches(edges, colors, chosen=None):
    """get a dictionary of branches from edges and colors and a banned edge"""

    branches: BranchDict = {}
    for color in Color:
        branches[color] = defaultdict(set)

    for i, ((a, b), color) in enumerate(zip(edges, colors), 1):
        if i == chosen:
            continue

        branches[color][a].add(b)
        branches[color][b].add(a)

    return branches


def draw_graph(graph: nx.Graph, pos, edges, colors):
    """draw a game of hackenbush"""
    graph.clear()

    nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color=colors)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=dict(map(reversed, enumerate(edges, 1))))

    plt.show()


def get_branch_choice(possible, player):
    print(f"{player}'s turn")
    print(f"possible moves: {possible}")
    while True:
        try:
            chosen_str = input("enter branch to cut or q to exit: ")

            # exit if q is chosen
            if chosen_str == "q":
                return None

            # retry if the chosen branch is invalid
            chosen = int(chosen_str)
            if chosen not in possible:
                raise ValueError
        except ValueError:
            print("invalid branch")
            continue

        return chosen


def game(edges, colors, player: Color, drawer, bot):
    """play a game of hackenbush"""
    # get a list of all the branches of the correct color
    possible = list(compress(count(1), map(partial(eq, player), colors)))

    # if the player can't make a move, the other one wins
    if not possible:
        print(f"{player.other} wins")
        return

    # get a branch to cut
    # implementation of the bot
    if bot == player: # player
        
        value, moves = simulated_game(edges, colors, player, float('-inf'), float('inf'))
        chosen = moves[-1]
        print(f"The value of the move is {value}.")
    
    else:
        chosen = get_branch_choice(possible, player)
    # exit if requested
    if chosen is None:
        return

    # get the branches that didn't fall
    edges, colors = get_edges(get_branches(edges, colors, chosen))

    # draw the graph
    drawer(edges, colors)

    # continue the game
    game(edges, colors, player.other, drawer, bot)

def simulated_game(edges, colors, player: Color, alpha, beta):
    '''Simulated game used by the minmax bot. If the position is won for blue, 
    it is a terminal node with value of +infinity, the inverse is true for read.'''
    possible = list(compress(count(1), map(partial(eq, player), colors)))

    # Triggers at terminal node, value of -100 for win for blue (player), 100 for red (bot)
    if not possible:
        if player == Color.BLUE: # Player loses 
            return 100, []
        else: # Bot loses
            return -100, []
    
    if player == Color.B:
        maxEval = float('-inf')
        max_moves = None
    else:
        minEval = float('inf')
        min_moves = None
    # Searches through every game in an dfs manner (implement alpha-beta pruning later)
    for branch in possible:
        chosen = branch 
        edges, colors = get_edges(get_branches(edges, colors, chosen))

        # dfs occurs
        value, moves = simulated_game(edges, colors, player.other, alpha, beta)
        
        # The longer the game, the more equal it is
        if value > 0:
            value -= 1
        else:
            value += 1
        
        moves.append(branch)

        if player == Color.B: # Maximizing player
            if value > maxEval:
                maxEval = value
                max_moves = moves

            alpha = max(alpha, value)
            if beta <= alpha:
                break
        else:
            if value < minEval:
                minEval = value
                min_moves = moves
            
            beta = min(beta, value)
            if beta <= alpha:
                break
    if player == Color.B:
        return maxEval, max_moves
    else:
        return min, min_moves




def level_maker():
    existing_nodes = 0 # Highest node value that exist, nodes are created in counting order
    edges = []
    colors = []
    while True:
        # Assign branch color
        color = None
        while color not in ['r', 'b', "R", "B"]:
            color = input("Please input a color (r, b): ")
        if color == 'b' or color == 'B':
            color = Color.B
        else:
            color = Color.R
        colors.append(color)

        # Assign edge
        start_n = -1
        while 0 > start_n or start_n > existing_nodes:
            try:
                start_n = int(input(f"Please choose a starting node {[n for n in range(existing_nodes+1)]}: "))
            except TypeError:
                print("Please input a valid node.")
        end_n = -1
        while 0 > end_n or end_n > existing_nodes + 1 or end_n == start_n:
            try:
                end_n = int(input(f"Please choose an end node {[n for n in range(existing_nodes+2) if n != start_n]}: "))
            except TypeError:
                print("Please input a valid node.")
        edges.append((start_n, end_n))
        # update list of nodes
        if end_n > existing_nodes:
            existing_nodes += 1

        if input("Do you wish to exit? (y, n): ")[0] in ['y', 'Y']:
            break
    return edges, colors


def rando_level_maker(red_br, blue_br):
    '''Creates a random level by alternating between adding a blue branch and 
    a red branch to an empty level. '''
    
    colors = []
    edges = []
    color = Color.R
    existing_nodes = 0 # the possible nodes are always the number of existing nodes +1
    while red_br > 0 or blue_br > 0:
        colors.append(color)
        if color == Color.R:
            red_br -= 1
            if blue_br != 0:
                color = Color.B
        else:
            blue_br -= 1
            if red_br != 0:
                color = Color.R

        start_n = random.randint(0, existing_nodes)
        end_n = random.randint(0, existing_nodes+1)
        while end_n == start_n or ((start_n, end_n) in edges):
            end_n = random.randint(0, existing_nodes + 1)
        if end_n == existing_nodes + 1:
            existing_nodes += 1
        edges.append((start_n, end_n))
    print(edges)
    print(colors)
    return edges, colors



# add branches for simulation
def premade(num):
    match num:
        case 1: # Level 1
            edges, colors = zip(*(
                ((0, 1), Color.B),
                ((1, 2), Color.R),
                ((1, 3), Color.B),
                ((3, 4), Color.R),

                ((0, 5), Color.R),
                ((5, 6), Color.B)
            ))
    return edges, colors

#edges, colors = level_maker()

#edges, colors = rando_level_maker(10, 10)
#print(edges, colors)

def make_game(edges, colors):
    # reorder the edges to draw them correctly
    edges, colors = get_edges(get_branches(edges, colors))

    # create a graph
    graph = nx.Graph(edges)

    # set the way the graph is displayed
    pos = nx.bfs_layout(graph, 0, align="horizontal")
    drawer = partial(draw_graph, graph, pos)

    # draw the graph
    drawer(edges, colors)
    return edges, colors, drawer
# start the game



#print(simulated_game(edges, colors, Color.BLUE))
''''''
def main():
    print('Welcome to Hackenbush!')
    choice = None
    while choice not in ['1', '2', '3', '4']:
        choice = input('''Please select one of the following:
                       1. Play the premade level against another player.
                       2. Play the premade level against the bot. 
                       3. Make your own level. 
                       4. Play a randomly generated level.
                       5. Quit.
                       Enter your choice (1,2,3,4,5): ''')
    match int(choice):
        case 1: # currently it is same as against bot
            edges, colors = premade(1)
            edges, colors, drawer = make_game(edges, colors)
            game(edges, colors, Color.BLUE, drawer, None)
        case 2:
            bot = None
            while bot not in ['b', 'B', 'r', 'R']:
                bot = input("Please select the bot color (r, b): ")
            if bot in ['r', 'R']:
                bot = Color.R
            else:
                bot = Color.B
            edges, colors = premade(1)
            edges, colors, drawer = make_game(edges, colors)
            game(edges, colors, Color.BLUE, drawer, bot)
        case 3:
            edges, colors = level_maker()
            edges, colors, drawer - make_game(edges, colors)
            game(edges, colors, Color.BLUE, drawer, None)
        case 4:
            edges, colors = rando_level_maker(10,10)
            edges, colors, drawer = make_game(edges, colors)
            game(edges, colors, Color.BLUE, drawer, None)
        case 5:
            quit()

if __name__ == '__main__':
    main()