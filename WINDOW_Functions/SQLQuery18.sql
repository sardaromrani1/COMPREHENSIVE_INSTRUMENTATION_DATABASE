-- 6. Running Total of Spare Parts used (supply-chain KPI)

-- Very useful in stock optimization.

SELECT 
    sp.SparePartID,
    sp.PartName,
    sp.AnnualUsage,
    SUM(sp.AnnualUsage) OVER (
        ORDER BY sp.SparePartID
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS RunningTotal
FROM SpareParts sp;
