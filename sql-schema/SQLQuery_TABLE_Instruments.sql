
CREATE TABLE Instruments (
    InstrumentID INT PRIMARY KEY IDENTITY(1,1),
    
    -- Identification
    TagNumber NVARCHAR(50) UNIQUE NOT NULL, -- FT-101A, PT-205B
    AlternateTag NVARCHAR(50), -- Old tag or customer tag
    SerialNumber NVARCHAR(100),
    AssetNumber NVARCHAR(50), -- Company asset number
    
    -- Location
    SiteID INT NOT NULL,
    UnitID INT NOT NULL,
    SubSystemID INT,
    SystemID INT,
    
    -- Classification
    InstrumentTypeID INT NOT NULL,
    ManufacturerID INT,
    
    -- Technical Details
    Manufacturer NVARCHAR(100),
    Model NVARCHAR(100),
    Description NVARCHAR(500),
    FunctionalDescription NVARCHAR(1000),
    
    -- Process Information
    ProcessVariable NVARCHAR(50), -- Flow, Pressure, Temperature, Level, etc.
    ServiceDescription NVARCHAR(200), -- What it measures: "Natural Gas Flow"
    FluidType NVARCHAR(100), -- Gas, Liquid, Steam, Slurry, etc.
    FluidComposition NVARCHAR(200),
    
    -- Measurement Range
    MeasurementRangeMin DECIMAL(18,4),
    MeasurementRangeMax DECIMAL(18,4),
    MeasurementUnit NVARCHAR(20),
    
    -- Output Range
    OutputRangeMin DECIMAL(18,4) DEFAULT 4, -- 4mA
    OutputRangeMax DECIMAL(18,4) DEFAULT 20, -- 20mA
    OutputUnit NVARCHAR(20) DEFAULT 'mA',
    
    -- Accuracy & Performance
    Accuracy NVARCHAR(50), -- ±0.1% of span
    Repeatability NVARCHAR(50),
    Rangeability NVARCHAR(50),
    ResponseTime NVARCHAR(50),
    
    -- Physical Location
    LocationDescription NVARCHAR(200),
    InstallationDrawing NVARCHAR(100), -- Drawing number
    PIDNumber NVARCHAR(50), -- P&ID drawing reference
    PipelineID NVARCHAR(50),
    ElevationLevel NVARCHAR(20),
    GridReference NVARCHAR(50), -- Plant grid location
    
    -- Installation Details
    MountingType NVARCHAR(50), -- In-line, Flange, Threaded, Remote Seal
    ProcessConnection NVARCHAR(50), -- 1/2" NPT, Flange 150#, etc.
    MaterialOfConstruction NVARCHAR(100),
    WetPartsMaterial NVARCHAR(100),
    GasketMaterial NVARCHAR(50),
    
    -- Electrical
    PowerSupply NVARCHAR(50), -- 24VDC, 110VAC, 220VAC, Loop Powered
    PowerConsumption NVARCHAR(50),
    SignalType NVARCHAR(50), -- 4-20mA, HART, Digital, Wireless
    CommunicationProtocol NVARCHAR(100),
    WiringDiagram NVARCHAR(100),
    JunctionBoxNumber NVARCHAR(50),
    CableTag NVARCHAR(50),
    CableType NVARCHAR(50),
    CableLength_Meters DECIMAL(10,2),
    
    -- I/O Assignment
    IOCardLocation NVARCHAR(50), -- Rack-Slot-Channel
    IOCardType NVARCHAR(50),
    DCSAddress NVARCHAR(100),
    ModbusAddress INT,
    
    -- Safety & Hazardous Area
    IsSafetyInstrument BIT DEFAULT 0,
    SIL_Rating NVARCHAR(10), -- SIL 1, 2, 3, 4
    SIF_Number NVARCHAR(50), -- Safety Instrumented Function
    ATEX_Rating NVARCHAR(50), -- Ex d IIC T6
    ATEX_Certificate NVARCHAR(100),
    IP_Rating NVARCHAR(10), -- IP65, IP67
    NEMA_Rating NVARCHAR(10),
    IECEx_Rating NVARCHAR(50),
    
    -- Alarms & Trips
    HasAlarm BIT DEFAULT 0,
    AlarmCount INT DEFAULT 0,
    HasTrip BIT DEFAULT 0,
    TripCount INT DEFAULT 0,
    IsInterlock BIT DEFAULT 0,
    
    -- Redundancy
    IsRedundant BIT DEFAULT 0,
    RedundantPair INT, -- InstrumentID of redundant pair
    RedundancyType NVARCHAR(20), -- Active/Standby, Voting (2oo3)
    
    -- Status
    Status NVARCHAR(20) DEFAULT 'Operational',
    -- Operational, Standby, Maintenance, Faulty, Bypassed, Decommissioned
    
    IsOperational BIT DEFAULT 1,
    IsByPassed BIT DEFAULT 0,
    ByPassReason NVARCHAR(500),
    ByPassDate DATETIME,
    ByPassApprovedBy NVARCHAR(100),
    
    -- Criticality
    Criticality NVARCHAR(20) DEFAULT 'Medium', -- Low, Medium, High, Critical
    FMEA_RPN INT, -- Failure Mode Effect Analysis - Risk Priority Number
    MaintenancePriority NVARCHAR(20),
    
    -- Dates
    PurchaseDate DATE,
    PurchaseOrderNumber NVARCHAR(50),
    PurchaseCost DECIMAL(18,2),
    CostCurrency NVARCHAR(10) DEFAULT 'USD',
    
    DeliveryDate DATE,
    InstallationDate DATE,
    CommissionDate DATE,
    StartupDate DATE,
    
    WarrantyPeriod_Months INT,
    WarrantyStartDate DATE,
    WarrantyExpiryDate DATE,
    IsUnderWarranty AS (CASE WHEN GETDATE() <= WarrantyExpiryDate THEN 1 ELSE 0 END),
    
    -- Calibration
    CalibrationRequired BIT DEFAULT 1,
    CalibrationInterval_Days INT,
    LastCalibrationDate DATE,
    CalibrationDueDate DATE,
    CalibrationStatus AS (
        CASE 
            WHEN CalibrationDueDate < GETDATE() THEN 'Overdue'
            WHEN CalibrationDueDate <= DATEADD(DAY, 30, GETDATE()) THEN 'Due Soon'
            ELSE 'Current'
        END
    ),
    NextCalibrationDate DATE,
    TotalCalibrationsPerformed INT DEFAULT 0,
    
    -- Maintenance
    MaintenanceInterval_Days INT,
    LastMaintenanceDate DATE,
    NextMaintenanceDate DATE,
    TotalMaintenancePerformed INT DEFAULT 0,
    
    -- Performance & Reliability
    InstallationRunningHours INT DEFAULT 0,
    TotalFailures INT DEFAULT 0,
    MTBF_Hours DECIMAL(10,2), -- Mean Time Between Failures
    MTTR_Hours DECIMAL(10,2), -- Mean Time To Repair
    Availability_Percent DECIMAL(5,2),
    
    -- Documentation
    DatasheetPath NVARCHAR(500),
    ManualPath NVARCHAR(500),
    DrawingPath NVARCHAR(500),
    CertificatePath NVARCHAR(500),
    
    -- Loop Details
    LoopNumber NVARCHAR(50),
    LoopDiagram NVARCHAR(100),
    IsPartOfControlLoop BIT DEFAULT 0,
    ControllerTag NVARCHAR(50),
    FinalControlElement NVARCHAR(50), -- Valve tag it controls
    
    -- Additional Info
    SpecialRequirements NVARCHAR(1000),
    OperatingInstructions NVARCHAR(2000),
    SafetyNotes NVARCHAR(1000),
    Notes NVARCHAR(MAX),
    
    -- Audit Trail
    CreatedBy NVARCHAR(100),
    CreatedDate DATETIME DEFAULT GETDATE(),
    ModifiedBy NVARCHAR(100),
    ModifiedDate DATETIME,
    
    -- Foreign Keys
    FOREIGN KEY (SiteID) REFERENCES Sites(SiteID),
    FOREIGN KEY (UnitID) REFERENCES ProcessUnits(UnitID),
    FOREIGN KEY (SubSystemID) REFERENCES SubSystems(SubSystemID),
    FOREIGN KEY (SystemID) REFERENCES ControlSystems(SystemID),
    FOREIGN KEY (InstrumentTypeID) REFERENCES InstrumentTypes(InstrumentTypeID),
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
    FOREIGN KEY (RedundantPair) REFERENCES Instruments(InstrumentID)
);
