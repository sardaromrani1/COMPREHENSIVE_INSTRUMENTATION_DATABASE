-- 3. Window Functions (Powerful!)
-- 3.1 ROW_NUMBER()

-- Goal: List instruments, but show the first instrument in every subsystem.

SELECT 
    i.TagNumber,
    ss.SubSystemName,
    ROW_NUMBER() OVER (PARTITION BY ss.SubSystemID ORDER BY i.TagNumber) AS RowNum
FROM Instruments i
JOIN SubSystems ss ON i.SubSystemID = ss.SubSystemID;
