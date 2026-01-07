-- Work Order Aging (How long WOs remain open)

CREATE OR ALTER VIEW v_WorkOrderAging AS
SELECT
    MaintenanceID,
    InstrumentID,
    WorkOrderNumber,
    Status,
    DATEDIFF(DAY, RequestedDate, ISNULL(CompletionDate, GETDATE())) AS Age_Days
FROM MaintenanceRecords;
