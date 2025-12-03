-- Inventory & Coverage KPIs
-- Instruments per Site / Process Unit / Subsystem (single query, aggregates + window)

WITH counts AS (
  SELECT 
    s.SiteID, s.SiteName,
    pu.UnitID, pu.UnitName,
    ss.SubSystemID, ss.SubSystemName,
    COUNT(i.InstrumentID) AS InstrumentsCount
  FROM SubSystems ss
  JOIN ProcessUnits pu ON ss.UnitID = pu.UnitID
  JOIN Sites s ON pu.SiteID = s.SiteID
  LEFT JOIN Instruments i ON i.SubSystemID = ss.SubSystemID
  GROUP BY s.SiteID, s.SiteName, pu.UnitID, pu.UnitName, ss.SubSystemID, ss.SubSystemName
)
SELECT
  SiteName,
  UnitName,
  SubSystemName,
  InstrumentsCount,
  SUM(InstrumentsCount) OVER (PARTITION BY SiteID) AS SiteTotalInstruments,
  SUM(InstrumentsCount) OVER (PARTITION BY SiteID, ProcessUnitID) AS UnitTotalInstruments,
  AVG(InstrumentsCount) OVER (PARTITION BY SiteID) AS AvgSubsystemsPerSite
FROM counts
ORDER BY SiteName, UnitName, InstrumentsCount DESC;
