USE ComprehensiveInstrumentationDB;
GO
-- 02_TABLE_InstrumentLifecycle.sql

/*===================================================================================================================
Table: InstrumentLifecycle
Layer: Lifecycle Model ( Layer2 )
Purpose:
	- Stores temporal state history of each instrument
	- Enables real MTBF, MTTR, Availability calculations
===================================================================================================================*/

CREATE TABLE dbo.InstrumentLifecycle(
	LifecycleID BIGINT IDENTITY(1, 1) PRIMARY KEY,
	InstrumentID INT NOT NULL,
	StateID INT NOT NULL,
	StateStartTime DATETIME2 NOT NULL,
	StateEndTime DATETIME2 NULL,
	ChangeReason NVARCHAR(255) NULL,
	SourceEventType NVARCHAR(50) NULL,
	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

	CONSTRAINT FK_InstrumentLifecycle_Instrument
		FOREIGN KEY (InstrumentID)
		REFERENCES ComprehensiveInstrumentationDB.dbo.Instruments(InstrumentID),

	CONSTRAINT FK_InstrumentLifecycle_State
		FOREIGN KEY (StateID)
		REFERENCES ComprehensiveInstrumentationDB.dbo.InstrumentState(StateID),

	CONSTRAINT CK_InstrumentLifecycle_Time
		CHECK (StateEndTime IS NULL OR StateEndTime > StateStartTime )
);
GO