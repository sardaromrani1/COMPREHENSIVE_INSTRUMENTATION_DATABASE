CREATE TABLE TripDefinition(
	TripID INT IDENTITY(1, 1) PRIMARY KEY,
	InstrumentID INT NOT NULL,
	RelatedAlarmConfigID INT NULL,
	ProtectionLevel NVARCHAR(50),	-- SIS, BPCS, Interlock
	ActionType NVARCHAR(50) NOT NULL,	-- Shutdown, Interlock, TripOnly
	Description NVARCHAR(255),
	IsActive BIT NOT NULL DEFAULT 1,
	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
	CONSTRAINT FK_TripDefinition_AlarmConfig
		FOREIGN KEY (RelatedAlarmConfigID)
		REFERENCES AlarmConfig(AlarmConfigID)
);