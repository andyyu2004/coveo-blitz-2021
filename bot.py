import game_command
from graph import Graph, bfs, get_adj, manhattan
from typing import List, Tuple, Set
from game_message import Depot, GameMessage, Position, Crew, Map, TileType, Unit, UnitType
from game_command import Action, UnitAction, UnitActionType, BuyAction
import random
import time


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
        # else
        elif crew_member.type == UnitType.OUTLAW:
            outlaws.append(crew_member)

    return miners, carts, outlaws


class Bot:

    graph: Graph
    game_message: GameMessage
    enemy_bases: Set[Position]
    occupied: Set[Position]
    # stores where carts are assigned to go
    cart_assignments: Set[Position]

    def init_cart_assignments(self):
        if self.game_message.tick > 1:
            return
        self.cart_assignments = set()

    def init_enemy_bases(self):
        # only run this once
        if self.game_message.tick > 1:
            return
        self.enemy_bases = set()
        for crew in self.game_message.crews:
            if crew.id == self.game_message.crewId:
                continue
            base = crew.homeBase
            for i in range(base.x - 3, base.x + 4):
                for j in range(base.y - 3, base.y + 4):
                    self.enemy_bases.add(Position(i, j))

    def is_occupied(self, position: Position) -> bool:
        return position in self.occupied

    def calculate_occupied(self):
        # occupied includes enemy base
        self.occupied = self.enemy_bases.copy()
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
        self.init_enemy_bases()
        self.calculate_occupied()
        self.init_cart_assignments()

        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        (miners, carts, outlaws) = separate_types(my_crew)
        mymap: Map = game_message.map

        """actions: List[UnitAction] = [UnitAction(UnitActionType.MOVE,
                                                miners[0].id,
                                                self.get_first_mine(mymap))]"""
        actions = []
        self.graph = Graph(game_message)
        # ratio of carts : miners
        cart_ratio = max(1, mymap.get_map_size() / 12)
        if game_message.tick < game_message.totalTick * 2 / 3:
            if cart_ratio*len(miners) <= len(carts) and my_crew.prices.MINER <= my_crew.blitzium:
                actions.append(BuyAction(UnitType.MINER))

            elif my_crew.prices.CART <= my_crew.blitzium and not (len(carts) >= cart_ratio*len(miners)):
                actions.append(BuyAction(UnitType.CART))

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
                    for j in miners + mymap.depots:
                        if j.blitzium > 0 and j.position == i:
                            actions.append(UnitAction(
                                UnitActionType.PICKUP, cart.id, j.position))
                            assigned = True
                            break
                if not assigned:
                    destination = self.get_adj_empty(
                        self.get_good_cart_objective(cart, my_crew), mymap)
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

    # takes current position of the cart and returns a "good" objective position
    def get_good_cart_objective(self, cart: Unit, crew: Crew) -> Position:

        position = cart.position
        mymap = self.game_message.map
        max_blitzium = -1
        best_miner = None
        for unit in crew.units:
            if unit.blitzium > max_blitzium and unit.position not in self.cart_assignments:
                max_blitzium = unit.blitzium
                best_miner = unit.position
        best_depot = None
        max_depot_blitzium = -1
        for depot in mymap.depots:
            # maybe its ok to send multiple carts to the same depot
            if depot.blitzium > max_depot_blitzium and manhattan(position, depot.position) <= 5:
                max_depot_blitzium = depot.blitzium
                best_depot = depot

        # if there is a best_depot and it is closer than the best_miner
        best = best_depot.position if best_depot and manhattan(
            position, best_depot.position) < manhattan(position, best_miner) else best_miner
        self.cart_assignments.add(best)
        return best

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
