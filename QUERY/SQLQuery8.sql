-- 3.3 LAG() / LEAD()

-- If you later add MaintenanceRecords, you can track trends.

-- Example (for future use):

SELECT 
    InstrumentID,
    CompletionDate,
    LAG(CompletionDate) OVER (PARTITION BY InstrumentID ORDER BY CompletionDate) AS PreviousMaintenance
FROM MaintenanceRecords;
