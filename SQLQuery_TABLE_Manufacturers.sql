-- ==========================================
-- 4. MANUFACTURERS & VENDORS - سازندگان
-- ==========================================

CREATE TABLE Manufacturers (
    ManufacturerID INT PRIMARY KEY IDENTITY(1,1),
    ManufacturerName NVARCHAR(100) UNIQUE NOT NULL,
    ShortName NVARCHAR(50),
    Country NVARCHAR(50),
    Website NVARCHAR(200),
    ContactEmail NVARCHAR(100),
    ContactPhone NVARCHAR(20),
    LocalRepresentative NVARCHAR(100),
    LocalRepPhone NVARCHAR(20),
    LocalRepEmail NVARCHAR(100),
    IsApprovedVendor BIT DEFAULT 1,
    QualityRating DECIMAL(3,2), -- 0.00 to 5.00
    DeliveryRating DECIMAL(3,2),
    TechnicalSupportRating DECIMAL(3,2),
    HasServiceCenter BIT DEFAULT 0,
    Notes NVARCHAR(1000)
);
