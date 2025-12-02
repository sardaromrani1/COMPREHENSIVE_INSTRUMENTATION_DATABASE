-- 1.3 FULL OUTER JOIN for gap analysis

-- Goal: Compare SubSystems vs Instruments to detect unused subsystem records.

SELECT 
    ss.SubSystemName,
    i.TagNumber
FROM SubSystems ss
FULL OUTER JOIN Instruments i 
    ON ss.SubSystemID = i.SubSystemID
ORDER BY ss.SubSystemName;
