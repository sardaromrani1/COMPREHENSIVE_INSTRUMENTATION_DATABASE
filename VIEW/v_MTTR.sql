-- MTTR (Mean Time To Repair)

-- View: MTTR per Instrument
CREATE OR ALTER VIEW v_MTTR AS
SELECT
    InstrumentID,
    AVG(DowntimeDuration_Hours * 1.0) AS MTTR_Hours
FROM MaintenanceRecords
WHERE DowntimeDuration_Hours IS NOT NULL
GROUP BY InstrumentID;
