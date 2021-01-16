from collections import deque
from game_message import GameMessage, Position, TileType
from typing import Deque, List, Tuple
import heapq


class Node:
    pos: Position
    # neighbors  : List[Node]

    def __init__(self,  pos: Position, tile_type: TileType):
        self.pos = pos
        self.neighbors = []
        self.tile_type = tile_type

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {len(self.neighbors)})"


class Graph:
    graph: List[List[Node]]

    def __init__(self, msg: GameMessage):
        mymap = msg.map
        game_size = mymap.get_map_size()
        self.graph = [[] for _ in range(game_size)]

        for i in range(game_size):
            for j in range(game_size):
                tile_type = mymap.get_raw_tile_value_at(Position(i, j))
                self.graph[i].append(Node(Position(i, j), tile_type))

        for i in range(game_size):
            for j in range(game_size):
                if j > 0 and mymap.get_tile_type_at(Position(i, j - 1)) == TileType.EMPTY:
                    self.graph[i][j].neighbors.append(self.graph[i][j - 1])

                if i < game_size - 1 and mymap.get_tile_type_at(Position(i + 1, j)) == TileType.EMPTY:
                    self.graph[i][j].neighbors.append(self.graph[i + 1][j])

                if j < game_size - 1 and mymap.get_tile_type_at(Position(i, j + 1)) == TileType.EMPTY:
                    self.graph[i][j].neighbors.append(self.graph[i][j + 1])

                if i > 0 and mymap.get_tile_type_at(Position(i - 1, j)) == TileType.EMPTY:
                    self.graph[i][j].neighbors.append(self.graph[i - 1][j])


def is_mine(node: Node, mygraph: Graph):
    return mygraph.graph[node.x][node.y].get_tile_type_at(Position(node.x, node.y)) == TileType.MINE


def manhattan(pos1: Position, pos2: Position):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def bfs(graph: Graph, start: Node, is_goal) -> Node:
    queue = deque()
    queue.append(start)
    visited = set()
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        if is_goal(node):
            return node
        for neighbor in node.neighbors:
            queue.append(neighbor)


# def a_star(graph: Graph, start: Node, is_goal):
#     pq: List[Tuple[int, Node]] = [0, start]
#     visited = {}
#     dist = {start: 0}
#     while pq:
#         (f_value, node) = heapq.heappop(pq)

#         if is_goal(node):
#             return node
#         for neighbor in node.neighbors:
#             heapq.heappush(pq, (weight, neighbor))
#         pass

"""
def a_star(graph: Graph, start: Node, end: Node):
    open_set = [start]
    distances = {start: 0}
    closed_set = []

    def get_best_node():
        best_distance = 10000
        best_node = open_set[0]
        for i in open_set:
            if distances[i] + manhattan(i.x, i.y, end.x, end.y) < best_distance:
                best_distance = distances[i] + \
                    manhattan(i.x, i.y, end.x, end.y) < best_distance
                best_node = i
        return best_node

    while open_set != []:
"""


# def find_miner():
#     crews = GameMessage.get_crews_by_id()
#     our_crew = crews[GameMessage.crewID]
#     our_units = our_crew.units
#     unit_types = [i.id for i in our_units]
#     print("Our crew is: " + str(unit_types))
