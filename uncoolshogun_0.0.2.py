import hlt
import logging
from collections import OrderedDict
import random
game = hlt.Game("UncoolShogun_v2")
logging.info("Starting SentdeBot")

while True:
    game_map = game.update_map()
    command_queue = []

    for ship in game_map.get_me().all_ships():
        shipid = ship.id
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]

        team_ships = game_map.get_me().all_ships()
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]

        # from conquest phase to brawl phase
        logging.info(ship.role)
        if len(closest_empty_planets) < len(game_map.all_planets())/2 and ship.role == 0:
            if random.random() > 0.2:
                logging.info("attack role")
                ship.role = 1
            else:
                logging.info("mine role")
                ship.role = -1

        # If there are any empty planets, let's try to mine!
        # make sure ship is still in conquest phase
        if ship.role != 1:
            target_planet = closest_empty_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                # don't be too close
                for other_ship in game_map.get_me().all_ships():
                    if other_ship.id == shipid:
                        continue
                    else:
                        if tooClose(ship, other_ship):
                            # evasion course !
                            logging.info("too close evasion course needed")
                navigate_command = ship.navigate(
                            ship.closest_point_to(target_planet),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command)

        # FIND SHIP TO ATTACK!
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]
            navigate_command = ship.navigate(
                        ship.closest_point_to(target_ship),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)

            if navigate_command:
                command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END


def tooClose (entityA,entityB):
    if entityA.calculate_distance_between(entityB) < entityA.radius + 1:
        return True
    else:
        return False
