-- ==========================================
-- 7. TRIPS & INTERLOCKS - تریپ و اینترلاک
-- ==========================================

CREATE TABLE TripsInterlocks (
    TripID INT PRIMARY KEY IDENTITY(1,1),
    TripTag NVARCHAR(50) UNIQUE NOT NULL,
    TripDescription NVARCHAR(500),
    TripType NVARCHAR(50), -- Process Shutdown, ESD, Interlock
    TripLogic NVARCHAR(1000), -- Logic description
    SIL_Level NVARCHAR(10),
    InitiatingInstruments NVARCHAR(500), -- List of instrument tags
    AffectedEquipment NVARCHAR(500),
    TripSetpoint DECIMAL(18,4),
    TripResetCondition NVARCHAR(500),
    IsAutoReset BIT DEFAULT 0,
    RequiresPermitToReset BIT DEFAULT 1,
    TestFrequency_Days INT,
    LastTestDate DATE,
    NextTestDate DATE,
    IsActive BIT DEFAULT 1
);
