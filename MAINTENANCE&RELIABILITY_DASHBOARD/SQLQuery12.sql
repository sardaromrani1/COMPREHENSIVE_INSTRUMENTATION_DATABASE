-- Repeated Corrective Maintenance (Bad Actors)

CREATE OR ALTER VIEW v_RepeatedCorrectiveMaintenance AS
SELECT
    InstrumentID,
    COUNT(*) AS CorrectiveCount
FROM MaintenanceRecords
WHERE MaintenanceType = 'Corrective'
  AND CompletionDate >= DATEADD(year, -1, GETDATE())
GROUP BY InstrumentID
HAVING COUNT(*) >= 3;
