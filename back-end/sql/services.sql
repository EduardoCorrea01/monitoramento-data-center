CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    endpoint_port VARCHAR(50),
    status ENUM('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
    response_time INT,
    last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_services_servers
        FOREIGN KEY (server_id)
        REFERENCES servers(id)
        ON DELETE CASCADE
);
