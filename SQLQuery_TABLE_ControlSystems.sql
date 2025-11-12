-- ==========================================
-- 2. CONTROL SYSTEMS - سیستم‌های کنترل
-- ==========================================

CREATE TABLE ControlSystems (
    SystemID INT PRIMARY KEY IDENTITY(1,1),
    UnitID INT,
    SystemCode NVARCHAR(20) UNIQUE NOT NULL,
    SystemName NVARCHAR(100) NOT NULL,
    SystemType NVARCHAR(50), -- DCS, PLC, SCADA, ESD, F&G, BMS, SIS
    Manufacturer NVARCHAR(100),
    Model NVARCHAR(100),
    SoftwareVersion NVARCHAR(50),
    FirmwareVersion NVARCHAR(50),
    InstallDate DATE,
    CommissionDate DATE,
    LastUpgradeDate DATE,
    RedundancyLevel NVARCHAR(20), -- None, Dual, Triple
    CommunicationProtocol NVARCHAR(100), -- Modbus, HART, Foundation Fieldbus, Profibus
    IsActive BIT DEFAULT 1,
    MaintenanceContract NVARCHAR(100),
    ContractExpiryDate DATE,
    FOREIGN KEY (UnitID) REFERENCES ProcessUnits(UnitID)
);
