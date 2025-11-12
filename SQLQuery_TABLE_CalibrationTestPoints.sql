-- Calibration Test Points
CREATE TABLE CalibrationTestPoints (
    TestPointID INT PRIMARY KEY IDENTITY(1,1),
    CalibrationID INT NOT NULL,
    TestSequence INT,
    AppliedInput DECIMAL(18,4),
    AsFoundOutput DECIMAL(18,4),
    AsLeftOutput DECIMAL(18,4),
    ExpectedOutput DECIMAL(18,4),
    AsFoundError DECIMAL(18,4),
    AsFoundError_Percent DECIMAL(5,2),
    AsLeftError DECIMAL(18,4),
    AsLeftError_Percent DECIMAL(5,2),
    IsWithinTolerance BIT,
    FOREIGN KEY (CalibrationID) REFERENCES CalibrationRecords(CalibrationID)
);
