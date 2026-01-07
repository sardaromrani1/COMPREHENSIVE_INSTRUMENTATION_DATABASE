-- Average Labor Hours per Work Order

CREATE OR ALTER VIEW v_AverageLaborHours AS
SELECT
    InstrumentID,
    AVG(LaborHours) AS AvgLaborHours
FROM MaintenanceRecords
WHERE LaborHours IS NOT NULL
GROUP BY InstrumentID;
