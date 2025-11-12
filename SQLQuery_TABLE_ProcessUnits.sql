-- Process Units
CREATE TABLE ProcessUnits (
    UnitID INT PRIMARY KEY IDENTITY(1,1),
    SiteID INT NOT NULL,
    UnitCode NVARCHAR(20) UNIQUE NOT NULL,
    UnitName NVARCHAR(100) NOT NULL,
    UnitType NVARCHAR(50),
    DesignCapacity DECIMAL(18,2),
    CapacityUnit NVARCHAR(20),
    OperatingPressure DECIMAL(10,2),
    OperatingTemperature DECIMAL(10,2),
    PressureUnit NVARCHAR(10) DEFAULT 'PSI',
    TemperatureUnit NVARCHAR(10) DEFAULT '°C',
    CommissionDate DATE,
    OperationalStatus NVARCHAR(20) DEFAULT 'Operational',
    HazardClass NVARCHAR(20),
    ATEX_Zone NVARCHAR(20),
    SIL_Level NVARCHAR(10),
    IsOperational BIT DEFAULT 1,
    FOREIGN KEY (SiteID) REFERENCES Sites(SiteID)
);
