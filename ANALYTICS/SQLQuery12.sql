-- 7 — Top-N & “Top 3 per Subsystem” (useful for spare allocation)
-- 7.1 Top 3 instrument types by count per subsystem (ROW_NUMBER)

WITH type_counts AS (
  SELECT ss.SubSystemID, ss.SubSystemName, it.TypeName, COUNT(i.InstrumentID) AS TypeCount,
    ROW_NUMBER() OVER (PARTITION BY ss.SubSystemID ORDER BY COUNT(i.InstrumentID) DESC) AS rn
  FROM SubSystems ss
  LEFT JOIN Instruments i ON i.SubSystemID = ss.SubSystemID
  LEFT JOIN InstrumentTypes it ON i.InstrumentTypeID = it.InstrumentTypeID
  GROUP BY ss.SubSystemID, ss.SubSystemName, it.TypeName
)
SELECT SubSystemName, TypeName, TypeCount
FROM type_counts
WHERE rn <= 3
ORDER BY SubSystemName, TypeCount DESC;
