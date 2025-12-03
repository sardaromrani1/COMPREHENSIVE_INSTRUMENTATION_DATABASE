-- Time-series & trends (installations, additions)
-- Monthly installations trend (last 24 months) + moving average (window)

WITH monthly AS (
  SELECT
    FORMAT(InstallationDate,'yyyy-MM') AS YearMonth,
    DATEFROMPARTS(YEAR(InstallationDate), MONTH(InstallationDate), 1) AS MonthStart,
    COUNT(*) AS Installs
  FROM Instruments
  WHERE InstallationDate IS NOT NULL
    AND InstallationDate >= DATEADD(month, -24, GETDATE())
  GROUP BY FORMAT(InstallationDate,'yyyy-MM'), DATEFROMPARTS(YEAR(InstallationDate), MONTH(InstallationDate), 1)
)
SELECT
  MonthStart,
  Installs,
  AVG(Installs) OVER (ORDER BY MonthStart ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS MovingAvg_3mo,
  SUM(Installs) OVER (ORDER BY MonthStart ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CumulativeInstalls
FROM monthly
ORDER BY MonthStart;
