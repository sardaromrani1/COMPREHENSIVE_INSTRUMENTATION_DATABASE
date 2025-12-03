-- Uptime % per Instrument

-- View: Uptime Percentage per Instrument
CREATE OR ALTER VIEW v_Uptime AS
WITH Failures AS (
    SELECT
        InstrumentID,
        FailureDate,
        LEAD(FailureDate) OVER(PARTITION BY InstrumentID ORDER BY FailureDate) AS NextFailureDate
    FROM FailureRecords
),
Intervals AS (
    SELECT
        InstrumentID,
        DATEDIFF(hour, FailureDate, ISNULL(NextFailureDate, GETDATE())) AS UptimeHours
    FROM Failures
)
SELECT
    I.InstrumentID,
    SUM(UptimeHours) AS TotalUptimeHours,
    SUM(UptimeHours) * 100.0 /
        DATEDIFF(hour, (SELECT MIN(FailureDate) 
                        FROM FailureRecords FR2 
                        WHERE FR2.InstrumentID = I.InstrumentID), GETDATE()) AS Uptime_Percentage
FROM Intervals I
GROUP BY I.InstrumentID;
