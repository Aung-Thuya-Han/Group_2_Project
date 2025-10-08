import random
import story
import mysql.connector
from dotenv import load_dotenv
import os
from typing import TypedDict, Optional, Any

load_dotenv()

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")


# Type definitions for database rows
class LocationRow(TypedDict):
    id: int
    name: str
    x_coord: int
    y_coord: int
    is_home: bool


class EventRow(TypedDict):
    id: int
    name: str
    money_change: int
    energy_change: int
    is_key: bool
    is_bully: bool
    description: str


class GameStateRow(TypedDict):
    id: int
    player_name: str
    money: int
    energy: int
    current_place: int
    key_found: bool


class RouteInfoRow(TypedDict):
    road_condition: str
    terrain_multiplier: float


class EventLocationRow(TypedDict):
    event_location_id: int
    name: str
    money_change: int
    energy_change: int
    is_key: bool
    is_bully: bool
    description: str


# Database connection
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    database="bike_in_town",
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    autocommit=True,
)


def get_locations() -> list[LocationRow]:
    """Get all locations from the database"""
    sql = "SELECT * FROM locations ORDER BY x_coord, y_coord"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result  # type: ignore


def get_events() -> list[EventRow]:
    """Get all events from the database"""
    sql = "SELECT * FROM events"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result  # type: ignore


def create_game(player_name: str, start_money: int, start_energy: int) -> int:
    """Create a new game instance"""
    # Get HOME location (id=1)
    home_location = 1

    with conn.cursor(dictionary=True) as cursor:
        sql = "INSERT INTO game (player_name, money, energy, current_place) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (player_name, start_money, start_energy, home_location))
        game_id = cursor.lastrowid
        if game_id is None:
            raise ValueError("Failed to create game: no game_id returned")

        # Randomly assign events to locations (excluding HOME)
        locations = get_locations()
        events = get_events()

        # Get non-home locations
        non_home_locations = [loc for loc in locations if not loc["is_home"]]
        random.shuffle(non_home_locations)

        # Assign events to random locations
        for i, event in enumerate(events):
            if i < len(non_home_locations):
                sql = "INSERT INTO event_locations (game_id, event_id, place_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, (game_id, event["id"], non_home_locations[i]["id"]))

    return game_id


def get_game_state(game_id: int) -> Optional[GameStateRow]:
    """Get current game state"""
    sql = "SELECT * FROM game WHERE id = %s"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql, (game_id,))
        result = cursor.fetchone()
    return result  # type: ignore


def get_location_info(location_id: int) -> Optional[LocationRow]:
    """Get location information"""
    sql = "SELECT * FROM locations WHERE id = %s"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql, (location_id,))
        result = cursor.fetchone()
    return result  # type: ignore


def calculate_manhattan_distance(loc1: LocationRow, loc2: LocationRow) -> int:
    """Calculate Manhattan distance between two locations"""
    return abs(loc1["x_coord"] - loc2["x_coord"]) + abs(
        loc1["y_coord"] - loc2["y_coord"]
    )


def get_route_info(from_location_id: int, to_location_id: int) -> RouteInfoRow:
    """Get route information between two locations"""
    sql = """SELECT road_condition, terrain_multiplier
             FROM routes
             WHERE from_location_id = %s \
               AND to_location_id = %s"""
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql, (from_location_id, to_location_id))
        result: Optional[Any] = cursor.fetchone()

    if result:
        return result  # type: ignore
    else:
        # Default road condition if no specific route exists
        return RouteInfoRow(road_condition="good", terrain_multiplier=1.0)


def calculate_energy_cost(current_location: LocationRow, target_location: LocationRow) -> int:
    """Calculate energy cost including route-specific road conditions"""
    base_distance = calculate_manhattan_distance(current_location, target_location)
    route_info = get_route_info(current_location["id"], target_location["id"])
    terrain_multiplier = route_info["terrain_multiplier"]
    return int(base_distance * terrain_multiplier)


def get_reachable_locations(current_location: LocationRow, all_locations: list[LocationRow], energy: int) -> list[dict[str, Any]]:
    """Get locations within energy range"""
    reachable: list[dict[str, Any]] = []
    for location in all_locations:
        if location["id"] != current_location["id"]:
            distance = calculate_manhattan_distance(current_location, location)
            energy_cost = calculate_energy_cost(current_location, location)
            if energy_cost <= energy:
                reachable.append(
                    {
                        "location": location,
                        "distance": distance,
                        "energy_cost": energy_cost,
                    }
                )
    return sorted(reachable, key=lambda x: x["energy_cost"])


def check_event_at_location(game_id: int, location_id: int) -> Optional[EventLocationRow]:
    """Check if there's an unresolved event at the current location"""
    sql = """SELECT el.id AS event_location_id, \
                    e.name, \
                    e.money_change, \
                    e.energy_change, \
                    e.is_key,
                    e.is_bully, \
                    e.description
             FROM event_locations el
                      JOIN events e ON el.event_id = e.id
             WHERE el.game_id = %s \
               AND el.place_id = %s \
               AND el.resolved = FALSE"""
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql, (game_id, location_id))
        result = cursor.fetchone()
    return result  # type: ignore


def resolve_event(event_location_id: int) -> None:
    """Mark an event as resolved"""
    sql = "UPDATE event_locations SET resolved = TRUE WHERE id = %s"
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(sql, (event_location_id,))


def update_game_state(game_id: int, money: Optional[int] = None, energy: Optional[int] = None, location: Optional[int] = None, key_found: Optional[bool] = None) -> None:
    """Update game state"""
    updates: list[str] = []
    values: list[Any] = []

    if money is not None:
        updates.append("money = %s")
        values.append(money)
    if energy is not None:
        updates.append("energy = %s")
        values.append(energy)
    if location is not None:
        updates.append("current_place = %s")
        values.append(location)
    if key_found is not None:
        updates.append("key_found = %s")
        values.append(key_found)

    if updates:
        sql = f"UPDATE game SET {', '.join(updates)} WHERE id = %s"
        values.append(game_id)
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(sql, values)


def display_map(current_location: LocationRow, all_locations: list[LocationRow], visited_locations: set[int]) -> None:
    """Display the town map"""
    print("\n🗺️  TOWN MAP")
    print("=" * 40)

    # Create a 5x5 grid display
    grid = [["." for _ in range(5)] for _ in range(5)]

    for location in all_locations:
        x, y = location["x_coord"], location["y_coord"]
        if location["id"] == current_location["id"]:
            grid[y][x] = "🏠" if location["is_home"] else "🚲"  # Current position
        elif location["id"] in visited_locations:
            grid[y][x] = "✓"  # Visited
        elif location["is_home"]:
            grid[y][x] = "🏠"  # Home
        else:
            grid[y][x] = "?"  # Unknown

    # Print grid with coordinates
    print("   0 1 2 3 4")
    for y in range(5):
        print(f"{y}  {' '.join(grid[y])}")

    print("\nLegend: 🏠=Home 🚲=You ✓=Visited ?=Unknown")


def show_locations(current_location: LocationRow, all_locations: list[LocationRow], energy: int) -> None:
    """Display reachable locations with energy costs and route-specific road conditions"""
    print("\n📍 REACHABLE DESTINATIONS")
    print("=" * 55)
    print(f"Current location: {current_location['name']}")
    print(f"Available energy: {energy}")
    print("\nReachable destinations:")
    print("Name".ljust(20) + "Energy Cost".ljust(12) + "Route Condition")
    print("-" * 55)

    reachable_count = 0
    for location in all_locations:
        energy_cost = calculate_energy_cost(current_location, location)
        if energy_cost <= energy:
            marker = (
                "🏠"
                if location["is_home"]
                else ("📍" if location["id"] == current_location["id"] else "  ")
            )
            route_info = get_route_info(current_location["id"], location["id"])
            road_condition = route_info["road_condition"]
            condition_icon = {
                "excellent": "🛣️",
                "good": "🚴",
                "poor": "⚠️",
                "rough": "🧗",
            }.get(road_condition, "🚴")

            print(
                f"{marker} {location['name'].ljust(18)} {str(energy_cost).ljust(10)} {condition_icon} {road_condition}"
            )
            reachable_count += 1

    if reachable_count == 1:  # Only current location
        print("No other locations within energy range!")
        print("💡 Tip: Use 'buy <amount>' to purchase energy drinks")

    print(f"\nShowing {reachable_count} reachable locations (out of 25 total)")
    print("Legend: 🏠=Home 📍=Current Location")
    print("Routes: 🛣️=Excellent ⚠️=Poor 🚴=Good 🧗=Rough")


def show_quick_info(game_state: GameStateRow, current_location: LocationRow) -> None:
    """Show quick status - location, money, and energy only"""
    print(
        f"📍 {current_location['name']} | 💰 ${game_state['money']} | ⚡ {game_state['energy']} energy"
    )


def handle_location_event(game_id: int, current_location: LocationRow) -> None:
    """Checks for and processes an event at the current location automatically."""
    game_state = get_game_state(game_id)
    if not game_state:
        print("Error: Game state not found.")
        return

    event = check_event_at_location(game_id, current_location["id"])
    if not event:
        print("Sorry! No event in this location.")
        return

    while True:
        choice = input(
            "There is an event here! Do you want to open it? (Y/N): "
        ).upper()
        if choice == "Y":
            event_location_id = event["event_location_id"]
            print(f"🗝️ {event['description']}")
            break
        elif choice == "N":
            print("You chose to skip the event for now!")
            return
        else:
            print("Please choose Y or N!")

    new_money = game_state["money"]
    new_energy = game_state["energy"]
    key_found = game_state["key_found"]

    # Get the correct ID for resolving the event

    if event["is_bully"]:
        print("💥 Oh no! You ran into a Bully! They took half your money.")
        money_lost = new_money // 2
        new_money = new_money - money_lost

    elif event["money_change"] != 0:
        new_money += event["money_change"]

    if event["energy_change"] != 0:
        new_energy += event["energy_change"]

    if event["is_key"]:
        key_found = True

    # Update state
    update_game_state(game_id, money=new_money, energy=new_energy, key_found=key_found)
    resolve_event(event_location_id)

    # Display changes
    if new_money != game_state["money"]:
        change = new_money - game_state["money"]
        print(f"💰 Money: ${game_state['money']} → ${new_money} ({change:+})")

    if new_energy != game_state["energy"]:
        change = new_energy - game_state["energy"]
        print(f"⚡️ Energy: {game_state['energy']} → {new_energy} ({change:+})")


def main_game() -> None:
    # Ask to show the story
    story_dialog = input("Do you want to read the background story? (Y/N): ").upper()
    if story_dialog == "Y":
        for line in story.get_story():
            print(line)
        input("\nPress Enter to continue...")

    # Game setup
    print("\n🚲 BIKE IN TOWN 🚲")
    print("Welcome to your adventure!")
    player_name = input("Enter your name: ")

    # Game settings
    start_money = 100
    start_energy = 100

    # Create new game
    game_id = create_game(player_name, start_money, start_energy)
    visited_locations = set([1])  # Start with HOME visited

    # Game state
    game_over = False

    print(
        f"\nGame started! You begin at HOME with ${start_money} and {start_energy} energy."
    )
    print("Type 'help' for available commands.")

    # Main game loop
    while not game_over:
        # Get current state
        game_state = get_game_state(game_id)
        if not game_state:
            print("Error: Game state not found.")
            break

        current_location = get_location_info(game_state["current_place"])
        if not current_location:
            print("Error: Current location not found.")
            break

        all_locations = get_locations()

        print(f"\n📍 You are at {current_location['name']}")

        # Get user command
        command = input("\nWhat would you like to do? ").lower().strip()

        if command == "help":
            print("\n🔧 AVAILABLE COMMANDS:")
            print("info - Show current location, money, and energy")
            print("map - Display the town map")
            print("locations - Show reachable locations within energy range")
            print("buy <amount> - Buy energy drinks (1$ = 1 energy)")
            print("move <location_name> - Move to a location")
            print("quit - Exit the game")

        elif command == "info":
            show_quick_info(game_state, current_location)

        elif command == "map":
            display_map(current_location, all_locations, visited_locations)

        elif command == "locations":
            show_locations(current_location, all_locations, game_state["energy"])

        elif command == "debug":
            print(f"DEBUG: Current location data: {current_location}")
            print(
                f"DEBUG: Sample location data: {all_locations[1] if len(all_locations) > 1 else 'None'}"
            )

        elif command.startswith("buy "):
            try:
                amount = int(command.split()[1])
                if amount <= 0:
                    print("❌ Please enter a positive amount.")
                elif amount > game_state["money"]:
                    print("❌ You don't have enough money.")
                else:
                    new_money = game_state["money"] - amount
                    new_energy = game_state["energy"] + amount
                    update_game_state(game_id, money=new_money, energy=new_energy)
                    print(
                        f"✅ Bought {amount} energy for ${amount}. Energy: {new_energy}, Money: ${new_money}"
                    )
            except (ValueError, IndexError):
                print("❌ Invalid format. Use: buy <amount>")

        elif command.startswith("move "):
            location_name = " ".join(command.split()[1:]).title()

            # Find the location
            target_location = None
            for loc in all_locations:
                if loc["name"].lower() == location_name.lower():
                    target_location = loc
                    break

            if not target_location:
                print(f"❌ Location '{location_name}' not found.")
                print("Available locations:")
                reachable = get_reachable_locations(
                    current_location, all_locations, game_state["energy"]
                )
                for option in reachable:
                    loc = option["location"]
                    print(
                        f"  - {loc['name']} (Distance: {option['distance']}, Energy cost: {option['energy_cost']})"
                    )
            else:
                energy_cost = calculate_energy_cost(current_location, target_location)
                if energy_cost > game_state["energy"]:
                    print(
                        f"❌ Not enough energy! Need {energy_cost}, have {game_state['energy']}"
                    )
                    route_info = get_route_info(
                        current_location["id"], target_location["id"]
                    )
                    road_condition = route_info["road_condition"]
                    if road_condition in ["poor", "rough"]:
                        print(
                            f"⚠️ The route from {current_location['name']} to {target_location['name']} has {road_condition} conditions!"
                        )
                else:
                    new_energy = game_state["energy"] - energy_cost
                    update_game_state(
                        game_id, energy=new_energy, location=target_location["id"]
                    )
                    visited_locations.add(target_location["id"])
                    route_info = get_route_info(
                        current_location["id"], target_location["id"]
                    )
                    road_condition = route_info["road_condition"]
                    road_msg = ""
                    if road_condition == "excellent":
                        road_msg = " (smooth ride! 🛣️)"
                    elif road_condition == "poor":
                        road_msg = " (bumpy route ⚠️)"
                    elif road_condition == "rough":
                        road_msg = " (rough terrain! 🧗)"
                    else:
                        road_msg = " (normal route 🚴)"
                    print(
                        f"🚲 Moved to {target_location['name']}{road_msg} Energy remaining: {new_energy}"
                    )
                    handle_location_event(game_id, target_location)
                # Check win/lose conditions
            game_state = get_game_state(game_id)
            if not game_state:
                print("Error: Game state not found.")
                break

            current_location = get_location_info(game_state["current_place"])
            if not current_location:
                print("Error: Current location not found.")
                break

            # Check if won (key found and at home)
            if game_state["key_found"] and current_location["is_home"]:
                print("\n🎉 CONGRATULATIONS! 🎉")
                print("You found the key and made it back home!")
                print(
                    f"Final score - Money: ${game_state['money']}, Energy: {game_state['energy']}"
                )
                game_over = True

                # Check if lost (no energy and no money, or can't reach home)

            if game_state["energy"] == 0 and game_state["money"] == 0:
                print("\n💀 GAME OVER!")
                print("You ran out of both energy and money!")
                game_over = True

            elif game_state["energy"] == 0:
                # Check if can buy energy
                if game_state["money"] == 0:
                    print("\n💀 GAME OVER!")
                    print("You ran out of energy and have no money to buy more!")
                    game_over = True
                else:
                    print(
                        "⚠️ Warning: You're out of energy! Use 'buy' command to purchase energy drinks."
                    )

        elif command == "quit":
            print("👋 Thanks for playing!")
            game_over = True

        else:
            print("❌ Unknown command. Type 'help' for available commands.")


if __name__ == "__main__":
    try:
        main_game()
    except KeyboardInterrupt:
        print("\n👋 Game interrupted. Thanks for playing!")
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        print("Make sure the database is set up correctly using database_setup.sql")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
