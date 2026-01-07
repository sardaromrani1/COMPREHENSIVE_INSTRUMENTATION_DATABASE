-- Preventive vs Corrective vs Breakdown Maintenance

CREATE OR ALTER VIEW v_MaintenanceTypeSummary AS
SELECT
    InstrumentID,
    MaintenanceType,
    COUNT(*) AS TotalJobs
FROM MaintenanceRecords
GROUP BY InstrumentID, MaintenanceType;
