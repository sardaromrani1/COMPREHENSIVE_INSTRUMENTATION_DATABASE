ALTER TABLE MaintenanceRecords
ADD FailureFlag AS 
(
    CASE 
        WHEN MaintenanceType IN ('Corrective', 'Breakdown')
             OR WorkOrderType IN ('CM', 'Breakdown')
             OR FailureMode IS NOT NULL
             OR RootCause IS NOT NULL
             OR (DowntimeStart IS NOT NULL AND DowntimeEnd IS NOT NULL)
        THEN 1 ELSE 0 
    END
);
