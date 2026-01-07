-- Maintenance Backlog (Open Work Orders)

CREATE OR ALTER VIEW v_MaintenanceBacklog AS
SELECT
    MaintenanceID,
    InstrumentID,
    WorkOrderNumber,
    Status,
    Priority,
    RequestedDate,
    AssignedTo
FROM MaintenanceRecords
WHERE Status NOT IN ('Completed', 'Cancelled');
