-- 1. Find the latest instrument added per SubSystem

-- Useful for monitoring new installations.

WITH LatestInstruments AS (
    SELECT 
        i.InstrumentID,
        i.TagNumber,
        ss.SubSystemName,
        i.CreatedDate,
        ROW_NUMBER() OVER (
            PARTITION BY i.SubSystemID 
            ORDER BY i.CreatedDate DESC
        ) AS rn
    FROM Instruments i
    JOIN SubSystems ss ON i.SubSystemID = ss.SubSystemID
)
SELECT *
FROM LatestInstruments
WHERE rn = 1;
