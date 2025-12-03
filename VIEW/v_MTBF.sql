-- MTBF (Mean Time Between Failures)

-- View: MTBF per Instrument
CREATE OR ALTER VIEW v_MTBF AS
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
