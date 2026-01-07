-- FailureMaintenanceLink.sql ( SQL Server )

CREATE TABLE FailureMaintenanceLink(
	FailureMaintenanceLinkID INT IDENTITY(1, 1) PRIMARY KEY,
	
	FailureEventID INT NOT NULL,
	MaintenanceEventID INT NOT NULL,

	LinkType NVARCHAR(50) NOT NULL,		-- Examples: 'Corrective', 'Inspection', 'TemporaryFix', 'Root Cause Repair'

	IsPrimaryFix BIT NOT NULL DEFAULT 0,
	Notes NVARCHAR(255) NULL,

	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

	CONSTRAINT FK_FailureMaintenanceLink_FailureEvent
		FOREIGN KEY (FailureEventID)
		REFERENCES FailureEvent(FailureEventID),

	CONSTRAINT FK_FailureMaintenanceLink_MaintenanceEvent
		FOREIGN KEY (MaintenanceEventID)
		REFERENCES MaintenanceEvent (MaintenanceEventID),

	CONSTRAINT UQ_FailiureMaintenanceLink
		UNIQUE (FailureEventID, MaintenanceEventID)
);