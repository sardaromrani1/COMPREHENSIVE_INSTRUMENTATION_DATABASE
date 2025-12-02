-- 4. Show % (percent) of total Instruments by Type

-- This is real KPI reporting.

WITH cte AS (
    SELECT 
        InstrumentTypeID,
        COUNT(*) AS TotalType,
        COUNT(*) OVER () AS TotalInstruments
    FROM Instruments
        
    GROUP BY InstrumentTypeID
)
SELECT 
    t.TypeName,
    TotalType,
    TotalInstruments,
    CAST(TotalType AS FLOAT) / TotalInstruments * 100 AS Percentage
FROM cte
JOIN InstrumentTypes t ON t.InstrumentTypeID = cte.InstrumentTypeID;
