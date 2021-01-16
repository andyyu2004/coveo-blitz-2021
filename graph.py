from collections import deque
from dataclasses import dataclass
from game_message import GameMessage, Map, Position, TileType
from typing import Deque, Dict, List, Tuple
import heapq


class Vertex:
    pos: Position
    tile_type: TileType

    def __init__(self, pos: Position, tile_type: TileType):
        self.pos = pos
        self.tile_type = tile_type


class Graph:
    adj: Dict[Position, List[Position]]

    def __init__(self, msg: GameMessage):
        adj: Dict[Position, [Position]] = {}
        for (i, row) in enumerate(msg.map.tiles):
            for (j, _tile) in enumerate(row):
                position = Position(i, j)
                adj[position] = []

        game_size = msg.map.get_map_size()
        for u in adj:
            for v in get_adj(u, game_size):
                if msg.map.get_tile_type_at(v) == TileType.EMPTY:
                    adj[u].append(v)

        self.adj = adj


def get_adj(pos: Position, game_size: int) -> List[Position]:
    adj = []
    i = pos.x
    j = pos.y
    if j > 0:
        adj.append(Position(i, j - 1))
    if i < game_size - 1:
        adj.append(Position(i + 1, j))
    if j < game_size - 1:
        adj.append(Position(i, j + 1))
    if i > 0:
        adj.append(Position(i - 1, j))
    return adj


def is_adj_to_tile_type(pos: Position, mymap: Map, tile_type: TileType) -> bool:
    for adj in get_adj(pos, mymap.get_map_size()):
        if mymap.get_tile_type_at(adj) == tile_type:
            return True
    return False


def manhattan(pos1: Position, pos2: Position):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def bfs(graph: Graph, start: Position, is_goal) -> Position:
    queue: Deque[Position] = deque()
    queue.append(start)
    visited = set()
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        if is_goal(node):
            return node
        for neighbor in graph.adj[node]:
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
