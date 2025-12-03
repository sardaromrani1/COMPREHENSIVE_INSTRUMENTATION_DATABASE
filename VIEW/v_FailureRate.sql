-- Failure Rate (Failures per Month)

-- View: Failure Rate per Month
CREATE OR ALTER VIEW v_FailureRate AS
SELECT
    FORMAT(FailureDate, 'yyyy-MM') AS FailureMonth,
    InstrumentID,
    COUNT(*) AS TotalFailures
FROM FailureRecords
GROUP BY FORMAT(FailureDate, 'yyyy-MM'), InstrumentID;
