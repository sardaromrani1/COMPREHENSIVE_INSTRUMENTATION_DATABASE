-- ==========================================
-- 10. FAILURE RECORDS - سوابق خرابی
-- ==========================================

CREATE TABLE FailureRecords (
    FailureID INT PRIMARY KEY IDENTITY(1,1),
    InstrumentID INT NOT NULL,
    MaintenanceID INT,
    
    -- Failure Details
    FailureDate DATETIME NOT NULL,
    DetectedDate DATETIME,
    ReportedDate DATETIME,
    DetectedBy NVARCHAR(100),
    DetectionMethod NVARCHAR(100), -- Operator Observation, Alarm, Inspection, etc.
    
    -- Failure Classification
    FailureMode NVARCHAR(200), -- Drift, No Output, Erratic, Zero Shift, etc.
    FailureType NVARCHAR(50), -- Mechanical, Electrical, Electronic, Software, Process
    FailureMechanism NVARCHAR(200), -- Wear, Corrosion, Fouling, Vibration, etc.
    FailureCause NVARCHAR(500),
    RootCause NVARCHAR(1000),
    
    -- Severity & Impact
    Severity NVARCHAR(20), -- Minor, Moderate, Major, Critical, Catastrophic
    SafetyImpact NVARCHAR(500),
    ProductionImpact NVARCHAR(500),
    EnvironmentalImpact NVARCHAR(500),
    FinancialImpact DECIMAL(18,2),
    
    -- Response
    ImmediateAction NVARCHAR(1000),
    BypassImplemented BIT DEFAULT 0,
    RedundantInstrumentActivated BIT DEFAULT 0,
    EmergencyShutdownTriggered BIT DEFAULT 0,
    
    -- Resolution
    ResolutionDate DATETIME,
    ResolutionDescription NVARCHAR(2000),
    MTTR_Hours AS (DATEDIFF(HOUR, FailureDate, ResolutionDate)),
    
    -- Analysis
    IsRepeatFailure BIT DEFAULT 0,
    PreviousFailureID INT,
    RepeatFailureCount INT DEFAULT 0,
    TimeSincePreviousFailure_Days INT,
    
    -- Cost
    RepairCost DECIMAL(18,2),
    ProductionLossCost DECIMAL(18,2),
    TotalCost AS (ISNULL(RepairCost,0) + ISNULL(ProductionLossCost,0)),
    
    -- Prevention
    PreventiveAction NVARCHAR(2000),
    DesignModificationRequired BIT DEFAULT 0,
    ProcedureUpdateRequired BIT DEFAULT 0,
    TrainingRequired BIT DEFAULT 0,
    
    -- Investigation
    InvestigationRequired BIT DEFAULT 0,
    InvestigationCompleted BIT DEFAULT 0,
    InvestigationReport NVARCHAR(500), -- File path
    
    Notes NVARCHAR(MAX),
    
    FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID),
    FOREIGN KEY (MaintenanceID) REFERENCES MaintenanceRecords(MaintenanceID),
    FOREIGN KEY (PreviousFailureID) REFERENCES FailureRecords(FailureID)
);

PRINT 'Comprehensive Instrumentation Database Created Successfully!';
PRINT 'Total Tables: 20+';
PRINT 'Ready for stored procedures and sample data...';