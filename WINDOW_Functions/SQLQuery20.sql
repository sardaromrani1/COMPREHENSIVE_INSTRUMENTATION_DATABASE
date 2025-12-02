-- 8. Find average number of instruments per subsystem (without GROUP BY)

-- This is very commonly used in dashboards

WITH SubsystemCounts AS (
    SELECT 
        ss.SubSystemID,
        ss.SubSystemName,
        COUNT(i.InstrumentID) AS InstrumentsInSubsystem
    FROM SubSystems ss
    LEFT JOIN Instruments i ON i.SubSystemID = ss.SubSystemID
    GROUP BY ss.SubSystemID, ss.SubSystemName
)
SELECT 
    SubSystemName,
    InstrumentsInSubsystem,
    AVG(InstrumentsInSubsystem) OVER () AS AvgSubsystemInstrumentCount
FROM SubsystemCounts;
