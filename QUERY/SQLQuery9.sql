-- 4. PIVOT / UNPIVOT
-- 4.1 PIVOT Example: Count instrument types by site

SELECT *
FROM (
    SELECT s.SiteName, t.TypeName
    FROM Instruments i
    JOIN Sites s ON i.SiteID = s.SiteID
    JOIN InstrumentTypes t ON i.InstrumentTypeID = t.InstrumentTypeID
) src
PIVOT (
    COUNT(TypeName) FOR TypeName IN ([Pressure], [Temperature], [Flow], [Level])
) AS pv;


-- (You can add your actual type names.)