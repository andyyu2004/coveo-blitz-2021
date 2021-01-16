from graph import Graph, bfs
from typing import List, Tuple
from game_message import GameMessage, Position, Crew, TileType, Unit, UnitType
from game_command import Action, UnitAction, UnitActionType
import random


class Bot:

    def get_next_move(self, game_message: GameMessage) -> List[Action]:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]

        g = Graph(game_message)

        ### my function ###

        # for nodes in g.graph:
        #     print(nodes)
        # actions = []
        # (miners, carts, outlaws) = separate_types(my_crew)
        # for miner in miners:
        #     nearby_mine = bfs(g, g.graph[miner.position.x][miner.position.y], lambda node: game_message.map.get_tile_type_at(
        #         node.pos) == TileType.MINE)
        #     actions.append(UnitAction(
        #         UnitActionType.MOVE, miner.id, nearby_mine))

        actions: List[UnitAction] = [UnitAction(UnitActionType.MOVE,
                                                unit.id,
                                                self.get_random_position(
                                                    game_message.map.get_map_size())) for unit in my_crew.units]

        return actions

    def get_random_position(self, map_size: int) -> Position:
        return Position(random.randint(0, map_size - 1), random.randint(0, map_size - 1))


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

    return (miners, carts, outlaws)


def get_miner_positions(crew: Crew):
    miners = []
    for crew_member in crew.units:
        if crew_member.type == UnitType.MINER:
            miners.append(crew_member.position)
