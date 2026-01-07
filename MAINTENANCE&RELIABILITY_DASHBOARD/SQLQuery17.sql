-- Root Cause Analysis Summary

CREATE OR ALTER VIEW v_RootCauseSummary AS
SELECT
    RootCauseCategory,
    COUNT(*) AS Occurrences
FROM MaintenanceRecords
WHERE RootCauseCategory IS NOT NULL
GROUP BY RootCauseCategory;
