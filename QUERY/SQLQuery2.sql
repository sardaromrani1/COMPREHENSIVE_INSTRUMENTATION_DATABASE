-- 1.2 LEFT JOIN for incomplete data

-- Goal: List all instruments including those without a subsystem.

SELECT 
    i.TagNumber,
    t.TypeName,
    ss.SubSystemName
FROM Instruments i
LEFT JOIN InstrumentTypes t ON i.InstrumentTypeID = t.InstrumentTypeID
LEFT JOIN SubSystems ss ON i.SubSystemID = ss.SubSystemID;
