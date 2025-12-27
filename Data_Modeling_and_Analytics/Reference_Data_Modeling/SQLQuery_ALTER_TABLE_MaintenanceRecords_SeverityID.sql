ALTER TABLE MaintenanceRecords
ADD CONSTRAINT FK_MaintenanceRecords_Severity
FOREIGN KEY (SeverityID)
REFERENCES Severity (SeverityID);