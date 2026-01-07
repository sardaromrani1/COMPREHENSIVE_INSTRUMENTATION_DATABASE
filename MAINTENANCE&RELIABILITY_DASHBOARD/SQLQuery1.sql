-- MTBF (Mean Time Between Failures)

-- MTBF per Instrument in hours (corrected)
WITH FailureIntervals AS (
    SELECT
        InstrumentID,
        DATEDIFF(hour,
                 LAG(FailureDate) OVER(PARTITION BY InstrumentID ORDER BY FailureDate),
                 FailureDate) AS IntervalHours
    FROM FailureRecords
)
SELECT
    InstrumentID,
    AVG(IntervalHours) AS MTBF_Hours
FROM FailureIntervals
WHERE IntervalHours IS NOT NULL
GROUP BY InstrumentID;
