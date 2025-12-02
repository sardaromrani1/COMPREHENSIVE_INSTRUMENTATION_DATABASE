-- 5.2 Forecast short-term demand using 3-month moving average per spare part

-- requires SparePartUsage(SparePartID, Quantity, UsageDate)
WITH monthly AS (
  SELECT
    SparePartID,
    DATEFROMPARTS(YEAR(UsageDate), MONTH(UsageDate), 1) AS MonthStart,
    SUM(Quantity) AS Used
  FROM SparePartUsage
  WHERE UsageDate >= DATEADD(month, -12, GETDATE())
  GROUP BY SparePartID, DATEFROMPARTS(YEAR(UsageDate), MONTH(UsageDate), 1)
),
ma AS (
  SELECT
    SparePartID, MonthStart, Used,
    AVG(Used) OVER (PARTITION BY SparePartID ORDER BY MonthStart ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS MA_3
  FROM monthly
)
SELECT SparePartID, MAX(MA_3) AS ForecastNextMonthEstimate
FROM ma
GROUP BY SparePartID
ORDER BY ForecastNextMonthEstimate DESC;
