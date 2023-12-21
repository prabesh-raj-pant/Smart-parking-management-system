
CREATE TABLE IF NOT EXISTS entry_exit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    parking_cost DECIMAL(10, 3) DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS parking_space (
    id INT AUTO_INCREMENT PRIMARY KEY,
    available_spaces INT NOT NULL,
    streets VARCHAR(30)
);
INSERT INTO parking_space(id,available_spaces,streets) VALUES (1,10,"street-1");

