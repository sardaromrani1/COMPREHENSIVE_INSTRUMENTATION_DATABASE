CREATE TABLE FailureMaintenanceLink(
	FailureID INT NOT NULL,
	MaintenanceID INT NOT NULL,
	IsPrimaryFix BIT DEFAULT 0,
	PRIMARY KEY(FailureID, MaintenanceID)
);