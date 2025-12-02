-- 5 — Spare Parts & Consumption Analytics
-- 5.1 Top spare parts by consumption and running total

WITH usage_totals AS (
  SELECT sp.SparePartID, sp.PartName, SUM(sp.AnnualUsage) AS TotalUsed
  FROM SpareParts sp
  GROUP BY sp.SparePartID, sp.PartName
)
SELECT
  SparePartID, PartName, TotalUsed,
  SUM(TotalUsed) OVER (ORDER BY TotalUsed DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CumulativeUsage,
  100.0 * TotalUsed / SUM(TotalUsed) OVER () AS PctOfTotal
FROM usage_totals
ORDER BY TotalUsed DESC;
