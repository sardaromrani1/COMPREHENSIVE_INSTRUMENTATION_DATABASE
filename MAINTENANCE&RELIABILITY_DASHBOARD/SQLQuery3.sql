-- Failure Rate

-- Failures per month
SELECT
    FORMAT(FailureDate,'yyyy-MM') AS Month,
    COUNT(*) AS TotalFailures
FROM FailureRecords
GROUP BY FORMAT(FailureDate,'yyyy-MM')
ORDER BY Month;
