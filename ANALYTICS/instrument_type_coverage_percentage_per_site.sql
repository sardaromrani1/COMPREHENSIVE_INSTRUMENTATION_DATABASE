-- % Coverage by Instrument Type per Site (percent of site total)

WITH t AS (
  SELECT
    s.SiteID, s.SiteName, it.InstrumentTypeID, it.TypeName,
    COUNT(i.InstrumentID) AS TypeCount
  FROM Instruments i
  JOIN Sites s ON i.SiteID = s.SiteID
  JOIN InstrumentTypes it ON i.InstrumentTypeID = it.InstrumentTypeID
  GROUP BY s.SiteID, s.SiteName, it.InstrumentTypeID, it.TypeName
)
SELECT
  SiteName, TypeName, TypeCount,
  SUM(TypeCount) OVER (PARTITION BY SiteID) AS SiteTotal,
  CAST(TypeCount AS FLOAT) / SUM(TypeCount) OVER (PARTITION BY SiteID) * 100.0 AS PctOfSite
FROM t
ORDER BY SiteName, PctOfSite DESC;
