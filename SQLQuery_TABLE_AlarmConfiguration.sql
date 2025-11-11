-- ==========================================
-- 6. ALARMS CONFIGURATION - تنظیمات آلارم
-- ==========================================

CREATE TABLE AlarmConfiguration (
    AlarmID INT PRIMARY KEY IDENTITY(1,1),
    InstrumentID INT NOT NULL,
    AlarmType NVARCHAR(50), -- HH, H, L, LL, Deviation, Rate of Change
    AlarmDescription NVARCHAR(200),
    AlarmSetpoint DECIMAL(18,4),
    AlarmDeadband DECIMAL(18,4),
    AlarmDelay_Seconds INT,
    AlarmPriority NVARCHAR(20), -- Low, Medium, High, Critical, Emergency
    AlarmAction NVARCHAR(500), -- What should operator do
    RequiresAcknowledgement BIT DEFAULT 1,
    IsEnabled BIT DEFAULT 1,
    EnabledDate DATE,
    DisabledDate DATE,
    DisabledBy NVARCHAR(100),
    DisabledReason NVARCHAR(500),
    FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
);
