-- Monthly Maintenance Trends

CREATE OR ALTER VIEW v_MaintenanceMonthlyTrend AS
SELECT
    FORMAT(RequestedDate, 'yyyy-MM') AS Month,
    COUNT(*) AS WorkOrders,
    SUM(ISNULL(LaborCost,0)) AS TotalLaborCost,
    SUM(ISNULL(PartsCost,0)) AS TotalPartsCost,
    SUM(TotalCost) AS TotalCost
FROM MaintenanceRecords
WHERE RequestedDate IS NOT NULL
GROUP BY FORMAT(RequestedDate, 'yyyy-MM');
