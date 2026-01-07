-- Uptime % per Instrument
-- Assuming your instrument is “up” until next failure:

-- Uptime % per Instrument
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
    InstrumentID,
    SUM(UptimeHours) AS TotalUptimeHours,
    SUM(UptimeHours) * 100.0 /
        DATEDIFF(hour, (SELECT MIN(FailureDate) 
                        FROM FailureRecords FR2 
                        WHERE FR2.InstrumentID = I.InstrumentID), GETDATE()) AS Uptime_Percentage
FROM Intervals I
GROUP BY InstrumentID;
