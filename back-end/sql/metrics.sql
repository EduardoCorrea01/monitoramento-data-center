CREATE TABLE IF NOT EXISTS metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    cpu_percent DECIMAL(5,2) NOT NULL,
    memory_percent DECIMAL(5,2) NOT NULL,
    disk_percent DECIMAL(5,2) NOT NULL,
    disk_total_gb DECIMAL(10,2) NULL,
    disk_used_gb DECIMAL(10,2) NULL,
    network_percent DECIMAL(5,2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_metrics_servers
        FOREIGN KEY (server_id)
        REFERENCES servers(id)
        ON DELETE CASCADE
);
