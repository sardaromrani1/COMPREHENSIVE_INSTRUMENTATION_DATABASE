-- 03_TABLE_FailureEvent.sql

CREATE TABLE FailureEvent(
	FailureEventID INT IDENTITY(1, 1) PRIMARY KEY,
	InstrumentID INT NOT NULL,
	FailureTypeID INT NOT NULL,		-- Lookup
	SeverityID INT NOT NULL,   -- FK to Severity


	FailureCause NVARCHAR(255) NULL,		-- Optional free text ( later can be coded )

	FailureStartTime DATETIME2 NOT NULL,
	FailureEndTime DATETIME2 NULL,		-- NULL = still failed

	DetectedBy NVARCHAR(100) NULL,		-- Operator / System / Alarm
	DetectionMethod NVARCHAR(100) NULL,		-- Alarm / Inspection / Trip

	IsSafetyRelated BIT NOT NULL DEFAULT 0,
	IsProductionImpact BIT NOT NULL DEFAULT 1,

	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

	CONSTRAINT FK_FailureEvent_Instrument
		FOREIGN KEY (InstrumentID)
		REFERENCES Instruments(InstrumentID),

	CONSTRAINT FK_FailureEvent_FailureType
		FOREIGN KEY (FailureTypeID)
		REFERENCES FailureType(FailureTypeID),

	CONSTRAINT FK_FailureEvent_Severity
		FOREIGN KEY (SeverityID)
		REFERENCES Severity (SeverityID),

	CONSTRAINT CK_FailureEvent_Time
		CHECK (FailureEndTime IS NULL OR FailureEndTime >= FailureStartTime)
);