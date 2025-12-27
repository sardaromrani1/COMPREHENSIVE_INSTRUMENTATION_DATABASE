ALTER TABLE MaintenanceRecords
ADD CONSTRAINT FK_MaintenanceRecords_Result
FOREIGN KEY (ResultID)
REFERENCES MaintenanceResult (ResultID);