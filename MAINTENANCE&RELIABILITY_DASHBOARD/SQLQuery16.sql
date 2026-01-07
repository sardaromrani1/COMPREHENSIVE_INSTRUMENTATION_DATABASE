-- Technician Performance

CREATE OR ALTER VIEW v_TechnicianPerformance AS
SELECT
    AssignedTo,
    COUNT(*) AS TotalJobs,
    SUM(LaborHours) AS TotalLaborHours,
    AVG(LaborHours) AS AvgLaborHours
FROM MaintenanceRecords
WHERE AssignedTo IS NOT NULL
GROUP BY AssignedTo;
