CREATE TABLE AlarmEvent(
	AlarmEventID BIGINT IDENTITY(1, 1) PRIMARY KEY,
	AlarmConfigID INT NOT NULL,
	EventTime DATETIME2 NOT NULL,
	MeasuredValue DECIMAL(18, 4) NOT NULL,
	IsAcknowledged BIT NOT NULL DEFAULT 0,
	AcknowledgedBy NVARCHAR(100),
	AcknowledgedTime DATETIME2,
	CONSTRAINT FK_AlarmEvent_AlarmConfig
		FOREIGN KEY (AlarmConfigID)
		REFERENCES AlarmConfig(AlarmConfigID)
);