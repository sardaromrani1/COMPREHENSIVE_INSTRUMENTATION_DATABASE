-- 3. Ranking SubSystems by the number of instruments

-- Maintenance teams often want to see busiest subsystems.

WITH cte AS (
    SELECT 
        SubSystemID,
        COUNT(*) AS TotalInstr
    FROM Instruments
    GROUP BY SubSystemID
)
SELECT 
    ss.SubSystemName,
    cte.TotalInstr,
    RANK() OVER (ORDER BY cte.TotalInstr DESC) AS RankByLoad
FROM cte
JOIN SubSystems ss ON ss.SubSystemID = cte.SubSystemID;
