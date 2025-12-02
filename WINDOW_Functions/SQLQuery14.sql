-- 2. Count instruments per site (but show count on every row)

-- Window functions let you avoid GROUP BY.

SELECT 
    s.SiteName,
    i.TagNumber,
    COUNT(*) OVER (PARTITION BY s.SiteID) AS InstrumentsInSite
FROM Instruments i
JOIN Sites s ON i.SiteID = s.SiteID;
