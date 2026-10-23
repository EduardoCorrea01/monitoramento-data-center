-- Run ONCE on an existing MySQL 'monitoring' database created from the old SQL.
-- Backup the database before applying. SQLite users should recreate only if needed;
-- ORM SQLite alert_type is VARCHAR(20) and already accepts AVAILABILITY.
USE monitoring;
ALTER TABLE alerts
    MODIFY COLUMN alert_type ENUM('CPU','MEMORY','DISK','AVAILABILITY') NOT NULL;
