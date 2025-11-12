CREATE TABLE TripInstruments (
    TripInstrumentID INT PRIMARY KEY IDENTITY(1,1),
    TripID INT NOT NULL,
    InstrumentID INT NOT NULL,
    VotingLogic NVARCHAR(20), -- 1oo1, 1oo2, 2oo3, etc.
    IsPrimary BIT DEFAULT 1,
    FOREIGN KEY (TripID) REFERENCES TripsInterlocks(TripID),
    FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
);
