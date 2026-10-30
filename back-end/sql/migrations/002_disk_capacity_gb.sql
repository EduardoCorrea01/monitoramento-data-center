ALTER TABLE metrics
    ADD COLUMN disk_total_gb DECIMAL(10,2) NULL,
    ADD COLUMN disk_used_gb DECIMAL(10,2) NULL;
