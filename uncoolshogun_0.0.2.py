import hlt
import logging
from collections import OrderedDict
game = hlt.Game("UncoolShogun_v2")
logging.info("Starting SentdeBot")

while True:
    game_map = game.update_map()
    command_queue = []

    # TODO:
    #Number of opponent
    #Number of planet by opponent
    #Number of ship by opponent

    for ship in game_map.get_me().all_ships():
        shipid = ship.id
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
        logging.info("number of empty planet : " + str(len(closest_empty_planets)))

        closest_owned_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].who_own() == game_map.get_me() and not entities_by_distance[distance][0].is_full()]
        logging.info("number of owned planets (! full): " +str(len(closest_owned_planets)))

        team_ships = game_map.get_me().all_ships()
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]
        logging.info("number of ennemy ship : "+ str(len(closest_enemy_ships)))
        # If there are any empty planets, let's try to mine!
        # make sure we are still in conquest phase
        if len(closest_empty_planets) + len(closest_owned_planets) > len(game_map.all_planets())/max((2*(len(game_map.all_players())-1)),2):
            if len(closest_owned_planets) > 0:
                # we want to fully load planet before expending but it need to be closer
                if ship.calculate_distance_between(closest_owned_planets[0]) > ship.calculate_distance_between(closest_empty_planets[0]):
                    target_planet = closest_empty_planets[0]
                else:
                    target_planet = closest_owned_planets[0]
            else:
                target_planet = closest_empty_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
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
