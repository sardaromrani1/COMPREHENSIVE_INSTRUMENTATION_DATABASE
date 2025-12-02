-- 7. Maintenance intervals per instrument (LAG + LEAD)

-- When you add a MaintenanceRecords table later, this becomes gold.

-- Example structure assumed:

-- MaintenanceRecords(RecordID, InstrumentID, MaintenanceDate)

SELECT
    InstrumentID,
    CompletionDate,
    LAG(CompletionDate) OVER (
        PARTITION BY InstrumentID ORDER BY CompletionDate
    ) AS PreviousMaintenance,
    DATEDIFF(day,
        LAG(CompletionDate) OVER (PARTITION BY InstrumentID ORDER BY CompletionDate),
        CompletionDate) AS DaysBetweenMaintenance
FROM MaintenanceRecords;
