# 🚲 Bike in Town

**Bike in Town** is a simple grid-based adventure game inspired by classic treasure
hunt mechanics.  
You start from HOME with some money and energy.

Your task: find the hidden **Key** somewhere in town and return safely back home
before you run out of resources.

---

## 🎮 Gameplay

- You always start at **HOME** with a small stash of **money** and **energy**.
- **Money** is used to buy **energy drinks** (money buys energy).
- **Energy** is used to ride your bike from one location to another
(movement cost = distance).
- Each location hides an **event** (reward or penalty). You can reveal it only once.
- Your goal is to:
  1. **Find the hidden Key.**
  2. **Ride back to HOME** with enough energy.

### Win condition

- Return to HOME with the Key → ✅ You win.

### Lose conditions

- Run out of **energy** with no money to buy more.
- Find the Key but can’t reach HOME due to lack of resources.

---

## ⚡ Events

Randomized across the map at the start of the game:

- 4 × $10 notes (+10 money)  
- 3 × $20 notes (+20 money)  
- 2 × Energy stash (+20 energy)  
- 2 × Bullies (lose half your money)  
- 2 × Flat tire (–10 money)  
- 1 × Crash (–20 energy)  
- 1 × Hidden Key (needed to win)

---

## 🕹️ Commands

If playing in the CLI version:

- `status` → Show your money, energy, location, key status.
- `map` → Display the town grid (visited locations marked).
- `buy <amount>` → Spend money to buy energy (1:1 by default).
- `move <location>` → Ride to another location (cost = distance).
- `open` → Reveal the event at the current location.
- `quit` → Exit the game.

---

## 🧩 How It Works

### Database Schema

- **locations**: all places on the map  
- **game**: player state (money, energy, location, key found)  
- **events**: possible events (cash, energy, bullies, etc.)  
- **event_locations**: randomized mapping of events → locations per game  

Check `tables_test.txt` for more details about the database tables.

### Movement Cost

- By default uses **Manhattan distance**:  

  ```math
  cost = |x2 - x1| + |y2 - y1|
  ```

---

## 🖥️ User Interface

**CLI (current):** text commands in terminal:

- `buy`: Use money to buy energy
- `plan`: See the cost of moving to a location
- `move`: Move to a location
- `help`: Display list of commands
- `quit`: Quit the game

---

## 🚀 Running the Game

### Requirements

- Python 3.10+ (for CLI prototype)
- MySQL or SQLite (for storing game state & map)

### Setup

```bash
git clone https://github.com/Aung-Thuya-Han/Group_2_Project.git
cd Group_2_Project

# create and activate venv (optional)
python -m venv .venv
source .venv/bin/activate
```
