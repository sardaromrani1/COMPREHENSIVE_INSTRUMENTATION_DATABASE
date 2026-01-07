-- Maintenance Costs Summary

CREATE OR ALTER VIEW v_MaintenanceCostSummary AS
SELECT
    InstrumentID,
    COUNT(*) AS WorkOrderCount,
    SUM(ISNULL(LaborCost,0)) AS TotalLaborCost,
    SUM(ISNULL(PartsCost,0)) AS TotalPartsCost,
    SUM(ISNULL(ContractorCost,0)) AS TotalContractorCost,
    SUM(ISNULL(OtherCosts,0)) AS TotalOtherCosts,
    SUM(TotalCost) AS TotalMaintenanceCost
FROM MaintenanceRecords
GROUP BY InstrumentID;
