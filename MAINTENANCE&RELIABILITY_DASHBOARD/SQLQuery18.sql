-- Maintenance Dashboard (All in One)

CREATE OR ALTER VIEW dbo.v_MaintenanceDashboard AS
SELECT
    mr.InstrumentID,
    mt.MTTR_Hours,
    dc.TotalDowntimeHours,
    cs.TotalMaintenanceCost,
    al.AvgLaborHours
FROM (SELECT DISTINCT InstrumentID FROM dbo.MaintenanceRecords) mr
LEFT JOIN dbo.v_MTTR mt ON mr.InstrumentID = mt.InstrumentID
LEFT JOIN dbo.v_DowntimeSummary dc ON mr.InstrumentID = dc.InstrumentID
LEFT JOIN dbo.v_MaintenanceCostSummary cs ON mr.InstrumentID = cs.InstrumentID
LEFT JOIN dbo.v_AverageLaborHours al ON mr.InstrumentID = al.InstrumentID;
