-- 9 — Combining PIVOT + Window: Dashboard-ready table
-- 9.1 Instruments by Type per Site (PIVOT)

SELECT SiteName, ISNULL([Pressure],0) AS Pressure, ISNULL([Flow],0) AS Flow, ISNULL([Level],0) AS Level, ISNULL([Temperature],0) AS Temperature
FROM (
  SELECT s.SiteName, it.TypeName
  FROM Instruments i
  JOIN Sites s ON i.SiteID = s.SiteID
  JOIN InstrumentTypes it ON i.InstrumentTypeID = it.InstrumentTypeID
) src
PIVOT (
  COUNT(TypeName) FOR TypeName IN ([Pressure], [Flow], [Level], [Temperature])
) AS p
ORDER BY SiteName;
