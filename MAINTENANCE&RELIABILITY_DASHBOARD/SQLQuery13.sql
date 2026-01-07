-- Downtime Summary per Instrument

CREATE OR ALTER VIEW v_DowntimeSummary AS
SELECT
    InstrumentID,
    COUNT(*) AS DowntimeEvents,
    SUM(DowntimeDuration_Hours) AS TotalDowntimeHours,
    AVG(DowntimeDuration_Hours) AS AvgDowntimeHours
FROM MaintenanceRecords
WHERE DowntimeStart IS NOT NULL AND DowntimeEnd IS NOT NULL
GROUP BY InstrumentID;
