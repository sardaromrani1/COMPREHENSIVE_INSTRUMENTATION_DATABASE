-- Instruments with Repeated Failures

-- Instruments failing more than 3 times in last year
SELECT
    InstrumentID,
    COUNT(*) AS FailureCount
FROM FailureRecords
WHERE FailureDate >= DATEADD(year, -1, GETDATE())
GROUP BY InstrumentID
HAVING COUNT(*) > 3
ORDER BY FailureCount DESC;
