-- 6 — Safety / Trip Instrument Analytics
-- 6.1 Trip instrument coverage per process unit (percent of instruments that are trip-capable)

WITH totals AS (
  SELECT
    pu.UnitID, pu.UnitName,
    COUNT(i.InstrumentID) AS TotalInstruments,
    SUM(CASE WHEN ti.InstrumentID IS NOT NULL THEN 1 ELSE 0 END) AS TripInstrumentCount
  FROM ProcessUnits pu
  JOIN SubSystems ss ON ss.UnitID = pu.UnitID
  LEFT JOIN Instruments i ON i.SubSystemID = ss.SubSystemID
  LEFT JOIN TripInstruments ti ON i.InstrumentID = ti.InstrumentID
  GROUP BY pu.UnitID, pu.UnitName
)
SELECT
  UnitName,
  TotalInstruments,
  TripInstrumentCount,
  CAST(TripInstrumentCount AS FLOAT) / NULLIF(TotalInstruments,0) * 100.0 AS TripCoveragePct
FROM totals
ORDER BY TripCoveragePct DESC;
