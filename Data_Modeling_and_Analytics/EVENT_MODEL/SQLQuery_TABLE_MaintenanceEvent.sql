-- 04_TABLE_MaintenanceEvent.sql

CREATE TABLE MaintenanceEvent(
	MaintenanceEventID INT IDENTITY(1, 1) PRIMARY KEY,

	InstrumentID INT NOT NULL,
	MaintenanceTypeID INT NOT NULL,			-- Lookup
	MaintenanceResultID INT NOT NULL,		-- Lookup ( Success, Temporary Fix / Failed )

	MaintenanceStartTime DATETIME2 NOT NULL,
	MaintenanceEndTime DATETIME2 NULL,

	PerformedBy NVARCHAR(150) NULL,			-- Team, Contractor, Technician
	WorkOrderNumber NVARCHAR(100) NULL,

	IsPlanned BIT NOT NULL DEFAULT 0,
	IsEmergency BIT NOT NULL DEFAULT 0,

	DowntimeHours DECIMAL(10, 2) NULL,
	LaborHours DECIMAL(10, 2) NULL,

	Notes NVARCHAR(500) NULL,

	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

	CONSTRAINT FK_MaintenanceEvent_Instrument 
		FOREIGN KEY (InstrumentID)
		REFERENCES Instruments(InstrumentID),

	CONSTRAINT FK_MaintenanceEvent_MaintenanceType
		FOREIGN KEY (MaintenanceTypeID)
		REFERENCES MaintenanceType (MaintenanceTypeID),

	CONSTRAINT FK_MaintenanceEvent_MaintenanceResult
		FOREIGN KEY (MaintenanceResultID)
		REFERENCES MaintenanceResult (ResultID),

	CONSTRAINT CK_MaintenanceEvent_Time
    CHECK(
        MaintenanceEndTime IS NULL
        OR MaintenanceEndTime >= MaintenanceStartTime
    )

);
