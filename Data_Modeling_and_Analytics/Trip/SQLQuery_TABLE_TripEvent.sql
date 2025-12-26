CREATE TABLE TripEvent(
	TripEventID BIGINT IDENTITY(1, 1) PRIMARY KEY,
	TripID INT NOT NULL,
	EventTime DATETIME2 NOT NULL,
	TriggerSource NVARCHAR(50),		-- Alarm, Sensor, Manual
	TripSeverity NVARCHAR(20),		-- Critical, Major, Minor
	ResetTime DATETIME2,
	CONSTRAINT FK_TripEvent_TripDefinition
		FOREIGN KEY (TripID)
		REFERENCES TripDefinition(TripID)
);