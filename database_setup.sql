-- Bike in Town Game Database Setup
-- Creates the database and tables needed for the game

CREATE DATABASE IF NOT EXISTS bike_in_town;
USE bike_in_town;

-- Drop tables if they exist (for clean setup)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS event_locations;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS game;
SET FOREIGN_KEY_CHECKS = 1;

-- Game table - stores player state
CREATE TABLE game (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(40) NOT NULL,
    money INT DEFAULT 100,
    energy INT DEFAULT 100,
    current_place INT NOT NULL,
    key_found BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations table - stores map locations (grid-based)
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    x_coord INT NOT NULL,
    y_coord INT NOT NULL,
    is_home BOOLEAN DEFAULT FALSE
);

-- Routes table - stores road conditions between specific location pairs
CREATE TABLE routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_location_id INT NOT NULL,
    to_location_id INT NOT NULL,
    road_condition ENUM('excellent', 'good', 'poor', 'rough') DEFAULT 'good',
    terrain_multiplier DECIMAL(3,2) DEFAULT 1.0,
    FOREIGN KEY (from_location_id) REFERENCES locations(id),
    FOREIGN KEY (to_location_id) REFERENCES locations(id),
    UNIQUE KEY unique_route (from_location_id, to_location_id)
);

-- Events table - stores event types
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    money_change INT DEFAULT 0,
    energy_change INT DEFAULT 0,
    is_key BOOLEAN DEFAULT FALSE,
    is_bully BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- Event_locations table - maps events to locations for each game
CREATE TABLE event_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    event_id INT NOT NULL,
    place_id INT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (game_id) REFERENCES game(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (place_id) REFERENCES locations(id)
);

-- Insert locations (5x5 grid)
INSERT INTO locations (name, x_coord, y_coord, is_home) VALUES
('HOME', 0, 0, TRUE),
('Park', 1, 0, FALSE),
('Market', 2, 0, FALSE),
('School', 3, 0, FALSE),
('Hospital', 4, 0, FALSE),
('Library', 0, 1, FALSE),
('Cafe', 1, 1, FALSE),
('Bank', 2, 1, FALSE),
('Post Office', 3, 1, FALSE),
('Police Station', 4, 1, FALSE),
('Gym', 0, 2, FALSE),
('Restaurant', 1, 2, FALSE),
('Store', 2, 2, FALSE),
('Theater', 3, 2, FALSE),
('Museum', 4, 2, FALSE),
('Playground', 0, 3, FALSE),
('Gas Station', 1, 3, FALSE),
('Mall', 2, 3, FALSE),
('Church', 3, 3, FALSE),
('Fire Station', 4, 3, FALSE),
('Beach', 0, 4, FALSE),
('Pier', 1, 4, FALSE),
('Lighthouse', 2, 4, FALSE),
('Marina', 3, 4, FALSE),
('Observatory', 4, 4, FALSE);

-- Insert event types
INSERT INTO events (name, money_change, energy_change, is_key, is_bully, description) VALUES
('$10 Note', 10, 0, FALSE, FALSE, 'You found a $10 note on the ground!'),
('$10 Note', 10, 0, FALSE, FALSE, 'You found a $10 note on the ground!'),
('$10 Note', 10, 0, FALSE, FALSE, 'You found a $10 note on the ground!'),
('$10 Note', 10, 0, FALSE, FALSE, 'You found a $10 note on the ground!'),
('$20 Note', 20, 0, FALSE, FALSE, 'You found a $20 note!'),
('$20 Note', 20, 0, FALSE, FALSE, 'You found a $20 note!'),
('$20 Note', 20, 0, FALSE, FALSE, 'You found a $20 note!'),
('Energy Stash', 0, 20, FALSE, FALSE, 'You found an energy drink stash!'),
('Energy Stash', 0, 20, FALSE, FALSE, 'You found an energy drink stash!'),
('Bullies', -50, 0, FALSE, TRUE, 'Bullies took half your money!'),
('Bullies', -50, 0, FALSE, TRUE, 'Bullies took half your money!'),
('Flat Tire', -10, 0, FALSE, FALSE, 'You got a flat tire and had to pay for repairs!'),
('Flat Tire', -10, 0, FALSE, FALSE, 'You got a flat tire and had to pay for repairs!'),
('Crash', 0, -20, FALSE, FALSE, 'You crashed and lost energy!'),
('Hidden Key', 0, 0, TRUE, FALSE, 'You found the hidden key! Now return home to win!');

-- Insert sample routes with varied road conditions
-- Note: Routes are bidirectional, so we need both directions for each pair
INSERT INTO routes (from_location_id, to_location_id, road_condition, terrain_multiplier) VALUES
-- From HOME (good connections to nearby places)
(1, 2, 'good', 1.0),      -- HOME to Park
(2, 1, 'good', 1.0),      -- Park to HOME
(1, 6, 'excellent', 0.8), -- HOME to Library (paved path)
(6, 1, 'excellent', 0.8), -- Library to HOME

-- Market connections (excellent main roads)
(2, 3, 'excellent', 0.8), -- Park to Market
(3, 2, 'excellent', 0.8), -- Market to Park
(3, 8, 'excellent', 0.8), -- Market to Bank
(8, 3, 'excellent', 0.8), -- Bank to Market

-- Poor road conditions to some locations
(6, 7, 'poor', 1.5),      -- Library to Cafe (bumpy side street)
(7, 6, 'poor', 1.5),      -- Cafe to Library
(7, 12, 'poor', 1.5),     -- Cafe to Restaurant
(12, 7, 'poor', 1.5),     -- Restaurant to Cafe

-- Rough terrain to remote locations
(16, 21, 'rough', 2.0),   -- Playground to Beach (dirt path)
(21, 16, 'rough', 2.0),   -- Beach to Playground
(21, 22, 'rough', 2.0),   -- Beach to Pier (sandy path)
(22, 21, 'rough', 2.0),   -- Pier to Beach
(22, 23, 'rough', 2.0),   -- Pier to Lighthouse (rocky coast)
(23, 22, 'rough', 2.0),   -- Lighthouse to Pier

-- Mixed conditions
(4, 5, 'good', 1.0),      -- School to Hospital
(5, 4, 'excellent', 0.8), -- Hospital to School (ambulance route)
(13, 14, 'poor', 1.5),    -- Store to Theater (construction zone)
(14, 13, 'good', 1.0),    -- Theater to Store (one-way better)

-- Gas Station has excellent roads (for emergency vehicles)
(17, 18, 'excellent', 0.8), -- Gas Station to Mall
(18, 17, 'excellent', 0.8), -- Mall to Gas Station
(17, 20, 'excellent', 0.8), -- Gas Station to Fire Station
(20, 17, 'excellent', 0.8); -- Fire Station to Gas Station