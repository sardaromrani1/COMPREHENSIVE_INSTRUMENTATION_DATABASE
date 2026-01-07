-- 02_TABLE_AssetEvent.sql
/*===================================================================================================================

Table: AssetEvent
Layer: Event Model (Layer 3)
Purpose: 
	- Stores all asset-related events in a unified structure
	- Supertype table for failure, maintenance, alarm, trip, etc.

====================================================================================================================*/
CREATE TABLE AssetEvent(
	EventID BIGINT IDENTITY(1, 1) PRIMARY KEY,
	InstrumentID INT NOT NULL,
	EventTypeID INT NOT NULL,
	EventStartTime DATETIME2 NOT NULL,
	EventEndTime DATETIME2 NULL,
	Severity NVARCHAR(50) NULL,
	Description NVARCHAR(500) NULL,
	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

	CONSTRAINT FK_AssetEvent_Instrument
		FOREIGN KEY (InstrumentID)
		REFERENCES Instruments(InstrumentID),

	CONSTRAINT FK_AssetEvent_EventType
		FOREIGN KEY (EventTypeID)
		REFERENCES EventType(EventTypeID),

	CONSTRAINT CK_AssetEvent_Time
		CHECK (EventEndTime IS NULL OR EventEndTime > EventStartTime)
);
GO