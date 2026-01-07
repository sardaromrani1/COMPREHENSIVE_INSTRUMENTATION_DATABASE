-- Maintenance Priority Distribution

CREATE OR ALTER VIEW v_MaintenancePriority AS
SELECT
    Priority,
    COUNT(*) AS TotalJobs
FROM MaintenanceRecords
GROUP BY Priority;
