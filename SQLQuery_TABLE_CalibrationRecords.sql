CREATE TABLE CalibrationRecords (
    CalibrationID INT PRIMARY KEY IDENTITY(1,1),
    InstrumentID INT NOT NULL,
    
    -- Scheduling
    ScheduledDate DATE,
    ActualDate DATETIME NOT NULL,
    NextDueDate DATE,
    
    -- Personnel
    CalibratedBy NVARCHAR(100),
    TechnicianID INT,
    SupervisedBy NVARCHAR(100),
    WitnessedBy NVARCHAR(100), -- For critical instruments
    
    -- Method & Standards
    CalibrationMethod NVARCHAR(100), -- As Per Manufacturer, ISO, etc.
    CalibrationProcedure NVARCHAR(100), -- Procedure document number
    ReferenceStandard NVARCHAR(200),
    ReferenceEquipmentID INT,
    ReferenceEquipmentTag NVARCHAR(50),
    ReferenceAccuracy NVARCHAR(50),
    TraceabilityCertificate NVARCHAR(100),
    
    -- Environmental Conditions
    AmbientTemperature DECIMAL(10,2),
    AmbientHumidity DECIMAL(5,2),
    AmbientPressure DECIMAL(10,2),
    
    -- Test Results
    TestPointsCount INT,
    PassedPoints INT,
    FailedPoints INT,
    
    AsFoundCondition NVARCHAR(50), -- Pass, Fail, Out of Tolerance
    AsFoundMaxError DECIMAL(18,4),
    AsFoundMaxError_Percent DECIMAL(5,2),
    
    AsLeftCondition NVARCHAR(50),
    AsLeftMaxError DECIMAL(18,4),
    AsLeftMaxError_Percent DECIMAL(5,2),
    
    AdjustmentRequired BIT DEFAULT 0,
    AdjustmentMade NVARCHAR(500),
    
    -- Tolerance & Uncertainty
    AcceptanceCriteria NVARCHAR(200),
    MeasurementUncertainty NVARCHAR(50),
    
    -- Status & Results
    CalibrationResult NVARCHAR(20), -- Pass, Fail, Limited Pass
    Status NVARCHAR(20) DEFAULT 'Completed',
    
    -- Documentation
    CertificateNumber NVARCHAR(100),
    CertificatePath NVARCHAR(500),
    IsAccreditedCalibration BIT DEFAULT 0,
    AccreditationBody NVARCHAR(100), -- ISO 17025, UKAS, etc.
    
    -- Time & Cost
    StartTime DATETIME,
    EndTime DATETIME,
    Duration_Minutes AS (DATEDIFF(MINUTE, StartTime, EndTime)),
    LaborCost DECIMAL(18,2),
    MaterialCost DECIMAL(18,2),
    TotalCost DECIMAL(18,2),
    
    -- Issues
    IssuesFound NVARCHAR(2000),
    CorrectiveActions NVARCHAR(2000),
    FollowUpRequired BIT DEFAULT 0,
    FollowUpDate DATE,
    
    Notes NVARCHAR(MAX),
    
    FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
);
