from collections import Set
from graph import Graph, bfs, get_adj
from typing import List, Tuple
from game_message import GameMessage, Position, Crew, Map, TileType, Unit, UnitType
from game_command import Action, UnitAction, UnitActionType, BuyAction
import random


def separate_types(crew: Crew) -> Tuple[List[Unit], List[Unit], List[Unit]]:
    """
    return (miners, carts, outlaws)
    """
    miners = []
    carts = []
    outlaws = []

    for crew_member in crew.units:
        if crew_member.type == UnitType.MINER:
            miners.append(crew_member)

        elif crew_member.type == UnitType.CART:
            carts.append(crew_member)

        elif crew_member.type == UnitType.OUTLAW:
            outlaws.append(crew_member)

    return miners, carts, outlaws


class Bot:

    graph: Graph
    game_message: GameMessage
    occupied: Set[Position]

    def is_occupied(self, position: Position) -> bool:
        return position in self.occupied

    def calculate_occupied(self):
        self.occupied = set()
        for crew in self.game_message.crews:
            for unit in crew.units:
                self.occupied.add(unit.position)

    def get_next_move(self, game_message: GameMessage) -> List[Action]:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """

        self.game_message = game_message
        self.calculate_occupied()

        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        (miners, carts, outlaws) = separate_types(my_crew)
        mymap: Map = game_message.map

        """actions: List[UnitAction] = [UnitAction(UnitActionType.MOVE,
                                                miners[0].id,
                                                self.get_first_mine(mymap))]"""
        actions = []
        self.graph = Graph(game_message)
        if len(miners) <= len(carts) and my_crew.prices.MINER <= my_crew.blitzium:
            actions.append(BuyAction(UnitType.MINER))

        if my_crew.prices.CART <= my_crew.blitzium and not (len(carts) >= len(miners)):
            actions.append(BuyAction(UnitType.CART))

        # if self.get_first_mine(mymap) and my_crew.prices.MINER < my_crew.blitzium:
        #     actions.append(BuyAction(UnitType.CART))

        for miner in miners:
            if self.is_adj_to_tile_type(miner.position, mymap, TileType.MINE):
                actions.append(UnitAction(
                    UnitActionType.MINE, miner.id, self.get_adj_mine(miner.position, mymap)))
            else:
                actions.append(UnitAction(UnitActionType.MOVE,
                                          miner.id, self.get_closest_mine(miner.position, mymap)))

        for cart in carts:
            if self.get_adj_home_base(cart.position, mymap, my_crew) and cart.blitzium != 0:
                actions.append(UnitAction(UnitActionType.DROP,
                                          cart.id, my_crew.homeBase))
            elif cart.blitzium != 0:
                actions.append(UnitAction(
                    UnitActionType.MOVE, cart.id, self.get_adj_empty(my_crew.homeBase, mymap)))
            else:
                assigned = False
                for i in get_adj(cart.position, mymap.get_map_size()):
                    for j in my_crew.units:
                        if j.blitzium > 0 and j.position == i and j.type != UnitType.MINER:
                            actions.append(UnitAction(
                                UnitActionType.PICKUP, cart.id, j.position))
                            assigned = True
                            break
                if not assigned:
                    destination = self.get_adj_empty(
                        self.get_richest_miner(my_crew), mymap)
                    actions.append(UnitAction(
                        UnitActionType.MOVE, cart.id, destination))

        return actions

    def get_random_position(self, map_size: int) -> Position:
        return Position(random.randint(0, map_size - 1), random.randint(0, map_size - 1))

    def is_adj_to_tile_type(self, pos: Position, mymap: Map, tile_type: TileType) -> bool:
        for adj in get_adj(pos, mymap.get_map_size()):
            if mymap.get_tile_type_at(adj) == tile_type:
                return True
        return False

    # returns a square adjacent to a mine
    def get_closest_mine(self, start: Position, mymap: Map) -> Position:
        return bfs(self.graph, start, lambda pos: self.is_adj_to_tile_type(pos, mymap, TileType.MINE) and not self.is_occupied(pos))

    def get_richest_miner(self, crew: Crew) -> Position:
        max_blitzium = -1
        for unit in crew.units:
            if unit.blitzium > max_blitzium:
                max_blitzium = unit.blitzium
                best_position = unit.position
        return best_position

    def get_adj_mine(self, pos: Position, mymap: Map) -> Position:
        for adj in get_adj(pos, mymap.get_map_size()):
            if mymap.get_tile_type_at(adj) == TileType.MINE:
                return adj

    def get_adj_home_base(self, pos: Position, mymap: Map, crew: Crew) -> Position:
        for adj in get_adj(pos, mymap.get_map_size()):
            if adj == crew.homeBase:
                return adj
        return None

    def get_adj_empty(self, pos: Position, mymap: Map) -> Position:
        for adj in get_adj(pos, mymap.get_map_size()):
            if mymap.get_tile_type_at(adj) == TileType.EMPTY and not self.is_occupied(adj):
                return adj
