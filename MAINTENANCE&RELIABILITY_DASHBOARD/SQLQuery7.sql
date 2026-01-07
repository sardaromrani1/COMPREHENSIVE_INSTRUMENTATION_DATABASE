-- Maintenance Completion Time (Work Order Duration)

CREATE OR ALTER VIEW v_MaintenanceDuration AS
SELECT
    MaintenanceID,
    InstrumentID,
    DATEDIFF(HOUR, RequestedDate, CompletionDate) AS RequestToCompletion_Hours,
    DATEDIFF(HOUR, StartDate, CompletionDate) AS StartToCompletion_Hours
FROM MaintenanceRecords
WHERE RequestedDate IS NOT NULL AND CompletionDate IS NOT NULL;
