-- Optional MySQL indexes. Execute only once after the tables exist.
CREATE INDEX idx_metrics_server_timestamp ON metrics(server_id, timestamp);
CREATE INDEX idx_alerts_server_status_type ON alerts(server_id, status, alert_type);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_events_server_timestamp ON events(server_id, timestamp);
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_servers_status_check ON servers(status, last_check);
