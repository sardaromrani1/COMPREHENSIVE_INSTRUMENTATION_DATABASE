-- 2.2 Recursive CTE (if you ever have hierarchy)

--Example: Control system → sub-units → components
-- (Useful for DCS hierarchies).

WITH ControlTree AS (
    SELECT SystemID, UnitID, SystemName
    FROM ControlSystems
    WHERE UnitID IS NULL
    
    UNION ALL
    
    SELECT c.SystemID, c.UnitID, c.SystemName
    FROM ControlSystems c
    INNER JOIN ControlTree ct ON ct.SystemID = c.UnitID
)
SELECT * FROM ControlTree;
