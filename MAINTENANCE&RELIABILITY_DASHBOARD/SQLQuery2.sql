-- MTTR (Mean Time To Repair)

-- MTTR per Instrument in hours
SELECT
    InstrumentID,
    AVG(DATEDIFF(hour, StartDate, CompletionDate) * 1.0) AS MTTR_Hours
FROM MaintenanceRecords
WHERE StartDate IS NOT NULL 
  AND CompletionDate IS NOT NULL
GROUP BY InstrumentID;
