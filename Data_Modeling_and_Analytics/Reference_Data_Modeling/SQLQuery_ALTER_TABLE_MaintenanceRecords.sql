-- Connecting Lookup tables to operational tables

ALTER TABLE MaintenanceRecords
ADD MaintenanceTypeID INT NULL,
	SeverityID INT NULL,
	ResultID INT NULL;