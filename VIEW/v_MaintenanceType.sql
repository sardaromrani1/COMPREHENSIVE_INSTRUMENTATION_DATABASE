-- Optional: Preventive vs Corrective Maintenance

-- View: Maintenance type summary per Instrument
CREATE OR ALTER VIEW v_MaintenanceType AS
SELECT
    InstrumentID,
    MaintenanceType,
    COUNT(*) AS TotalMaintenance
FROM MaintenanceRecords
GROUP BY InstrumentID, MaintenanceType;
