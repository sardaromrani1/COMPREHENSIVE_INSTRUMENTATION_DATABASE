-- 4 — Maintenance & Reliability (if you add MaintenanceRecords)
-- 4.1 Mean Time Between Failures (MTBF) & Mean Time To Repair (MTTR) per instrument

WITH failures AS (
  SELECT InstrumentID, CompletionDate, DowntimeDuration_Hours,
    ROW_NUMBER() OVER (PARTITION BY InstrumentID ORDER BY CompletionDate) AS rn
  FROM MaintenanceRecords
  WHERE FailureFlag = 1
),
paired AS (
  SELECT
    f.InstrumentID,
    f.CompletionDate AS FailureDate,
    LEAD(f.CompletionDate) OVER (PARTITION BY f.InstrumentID ORDER BY f.CompletionDate) AS NextFailureDate,
    f.DowntimeDuration_Hours
  FROM failures f
)
SELECT
  InstrumentID,
  AVG(DATEDIFF(hour, FailureDate, NextFailureDate)) / 24.0 AS AvgDaysBetweenFailures, -- MTBF in days
  AVG(DowntimeDuration_Hours) AS MTTR_Hours
FROM paired
WHERE NextFailureDate IS NOT NULL
GROUP BY InstrumentID
ORDER BY AvgDaysBetweenFailures ASC;
