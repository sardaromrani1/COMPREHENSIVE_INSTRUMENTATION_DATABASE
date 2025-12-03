-- Instruments with Repeated Failures

-- View: Instruments with frequent failures in the last 12 months
CREATE OR ALTER VIEW v_RepeatedFailures AS
SELECT
    InstrumentID,
    COUNT(*) AS FailureCount
FROM FailureRecords
WHERE FailureDate >= DATEADD(year, -1, GETDATE())
GROUP BY InstrumentID
HAVING COUNT(*) > 3;
