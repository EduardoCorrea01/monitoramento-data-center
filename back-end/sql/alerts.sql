-- For NEW MySQL installations. Use migrations/001_availability_alert.sql for existing DB.
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    alert_type ENUM('CPU','MEMORY','DISK','AVAILABILITY') NOT NULL,
    level ENUM('ALERT','CRITICAL') NOT NULL,
    message VARCHAR(255),
    status ENUM('ACTIVE','RESOLVED') DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerts_servers
        FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);
