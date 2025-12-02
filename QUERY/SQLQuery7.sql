-- 3.2 RANK()

-- Goal: Rank subsystems by number of instruments.

WITH CountCTE AS (
    SELECT SubSystemID, COUNT(*) AS Total
    FROM Instruments
    GROUP BY SubSystemID
)
SELECT 
    ss.SubSystemName,
    c.Total,
    RANK() OVER (ORDER BY c.Total DESC) AS RankByInstrumentCount
FROM CountCTE c
JOIN SubSystems ss ON c.SubSystemID = ss.SubSystemID;
