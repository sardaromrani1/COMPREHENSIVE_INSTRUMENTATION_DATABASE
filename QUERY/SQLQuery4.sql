-- 2.1 CTE for grouping

-- Goal: Count instruments per process unit.

WITH InstrumentCount AS (
    SELECT UnitID, COUNT(*) AS TotalInstruments
    FROM Instruments
    GROUP BY UnitID
)
SELECT pu.UnitName, ic.TotalInstruments
FROM InstrumentCount ic
JOIN ProcessUnits pu ON ic.UnitID = pu.UnitID;
