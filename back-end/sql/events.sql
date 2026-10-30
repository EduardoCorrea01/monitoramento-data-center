CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    history VARCHAR(255) NOT NULL,
    unavailable BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_events_servers
        FOREIGN KEY (server_id)
        REFERENCES servers(id)
        ON DELETE CASCADE
);
