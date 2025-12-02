-- 4.2 Rolling count of failures (last 365 days) per subsystem (window + partition)

WITH recent_failures AS (
  SELECT mr.MaintenanceID, mr.InstrumentID, mr.CompletionDate, i.SubSystemID
  FROM MaintenanceRecords mr
  JOIN Instruments i ON mr.InstrumentID = i.InstrumentID
  WHERE mr.FailureFlag = 1
    AND mr.CompletionDate >= DATEADD(day, -365, GETDATE())
)
SELECT
  SubSystemID,
  COUNT(*) AS FailuresLast365,
  RANK() OVER (ORDER BY COUNT(*) DESC) AS SubsystemRank
FROM recent_failures
GROUP BY SubSystemID
ORDER BY FailuresLast365 DESC;
