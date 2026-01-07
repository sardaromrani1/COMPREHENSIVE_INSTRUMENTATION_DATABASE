-- Instrument Lifecycle History Table

CREATE TABLE InstrumentLifecycle(
	LifecycleID INT IDENTITY PRIMARY KEY,
	InstrumentID INT NOT NULL,
	StatusCode VARCHAR(30) NOT NULL,	-- Installed, InService, OutOfService, Decommissioned
	StatusStartDate DATETIME NOT NULL,
	StatusEndDate DATETIME NULL,
	Reason NVARCHAR(255) NULL,
	ChangedBy NVARCHAR(100) NULL,

	CONSTRAINT FK_Lifecycle_Instrument
		FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
);