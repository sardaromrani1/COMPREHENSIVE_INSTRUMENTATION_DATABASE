-- 1.1 INNER JOIN with multiple relationships

-- Goal: Show instruments with their type, site, subsystem, and manufacturer.

SELECT 
    i.InstrumentID,
    i.TagNumber,
    t.TypeName AS InstrumentType,
    s.SiteName,
    ss.SubSystemName,
    m.ManufacturerName
FROM Instruments i
INNER JOIN InstrumentTypes t     ON i.InstrumentTypeID = t.InstrumentTypeID
INNER JOIN Sites s               ON i.SiteID = s.SiteID
INNER JOIN SubSystems ss         ON i.SubSystemID = ss.SubSystemID
INNER JOIN Manufacturers m       ON i.ManufacturerID = m.ManufacturerID;
