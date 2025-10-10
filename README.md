# 🚲 Bike in Town - Setup Instructions

This is the implementation of the "Bike in Town" game based on the requirements in README.md, using the flight simulator example as a model.

## Prerequisites

- Python 3.10+
- MySQL Server running locally
- MySQL root access (or configured user)

## Setup Instructions

### 1. Database Setup

```bash
# Connect to MySQL as root
mysql -u root -p

# Run the database setup script
source database_setup.sql

# Or manually:
mysql -u root -p < database_setup.sql
```

### 2. Python Environment Setup

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Set up your database credentials:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your MySQL credentials
vim .env  # or use your preferred editor
```

Example `.env` file:

```bash
DATABASE_USERNAME=root
DATABASE_PASSWORD=your_mysql_password
```

**Note:** The game will use `root` with no password by default
if no `.env` file exists.

### 4. Run the Game

```bash
python game.py
```

## Game Features

### Map

- 5x5 grid layout (25 locations)
- HOME is at coordinates (0,0)
- Manhattan distance movement system

### Resources

- **Money**: Used to buy energy drinks
- **Energy**: Consumed when moving (cost = Manhattan distance)

### Events (15 total, randomly distributed)

- 4x $10 notes (+$10)
- 3x $20 notes (+$20)
- 2x Energy stash (+20 energy)
- 2x Bullies (lose half money)
- 2x Flat tire (-$10)
- 1x Crash (-20 energy)
- 1x Hidden Key (win condition)

### Commands

- `info` - Show current location, money, and energy
- `map` - Display town map with visited locations
- `locations` - Show reachable locations within energy range
- `buy <amount>` - Buy energy drinks ($1 = 1 energy)
- `move <location_name>` - Move to a location
- `open` - Check for events at current location
- `help` - Show available commands
- `quit` - Exit game

### Route-Based Road Conditions & Movement Cost

Energy cost depends on the **specific route** between your starting point and destination:

#### Energy Cost = Manhattan Distance × Route Terrain Multiplier

**Route Conditions:**

- 🛣️ **Excellent** (0.8x) - Main roads, paved paths, ambulance routes
- 🚴 **Good** (1.0x) - Normal residential streets, standard energy cost
- ⚠️ **Poor** (1.5x) - Side streets, construction zones, bumpy roads
- 🧗 **Rough** (2.0x) - Dirt paths, sandy beaches, rocky coastlines

**Route Examples:**
- HOME → Library: Excellent paved path (1 × 0.8 = 1 energy)

- Library → Cafe: Poor side street (1 × 1.5 = 2 energy)
- Hospital → School: Excellent ambulance route (1 × 0.8 = 1 energy)
- School → Hospital: Good regular route (1 × 1.0 = 1 energy)
- Beach → Pier: Rough sandy path (1 × 2.0 = 2 energy)

**Key Features:**

- Routes are **bidirectional** but may have different conditions each way
- Some routes have excellent infrastructure (emergency services, main roads)
- Remote coastal areas have rough terrain requiring more energy
- Construction zones and side streets create poor conditions

### Win/Lose Conditions

- **Win**: Find the key AND return to HOME
- **Lose**: Run out of energy with no money to buy more

## Database Schema

The game uses 5 tables:
- `game` - Player state
- `locations` - Map locations (25 locations in 5x5 grid)
- `routes` - Road conditions between location pairs (bidirectional)
- `events` - Event types (15 different events)
- `event_locations` - Maps events to locations per game

## Example Gameplay

```bash
🚲 BIKE IN TOWN 🚲
Enter your name: Alice

📍 You are at HOME
What would you like to do? map

🗺️  TOWN MAP
   0 1 2 3 4
0  🚲 ? ? ? ?
1  ? ? ? ? ?
2  ? ? ? ? ?
3  ? ? ? ? ?
4  ? ? ? ? ?

What would you like to do? move park
🚲 Moved to Park. Energy remaining: 99

What would you like to do? open
🎁 You found a $10 note on the ground!
💰 Money: 100 → 110 (+10)
```
