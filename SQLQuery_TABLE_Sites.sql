
-- Site/Plant Level
CREATE TABLE Sites (
    SiteID INT PRIMARY KEY IDENTITY(1,1),
    SiteCode NVARCHAR(20) UNIQUE NOT NULL,
    SiteName NVARCHAR(100) NOT NULL,
    SiteType NVARCHAR(50), -- Refinery, Petrochemical, Power Plant, etc.
    Location NVARCHAR(200),
    Country NVARCHAR(50),
    GPS_Latitude DECIMAL(10,8),
    GPS_Longitude DECIMAL(11,8),
    Capacity NVARCHAR(100),
    CommissionDate DATE,
    IsActive BIT DEFAULT 1
);