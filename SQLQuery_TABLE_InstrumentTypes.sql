
-- ==========================================
-- 3. INSTRUMENT TYPES - انواع ابزار دقیق
-- ==========================================

CREATE TABLE InstrumentTypes (
    InstrumentTypeID INT PRIMARY KEY IDENTITY(1,1),
    TypeCode NVARCHAR(20) UNIQUE NOT NULL, -- FT, PT, TT, LT, AT, etc.
    TypeName NVARCHAR(100) NOT NULL,
    Category NVARCHAR(50), -- Measurement, Control, Safety, Analyzer, Actuator
    SubCategory NVARCHAR(50),
    Description NVARCHAR(500),
    MeasurementPrinciple NVARCHAR(100), -- Differential Pressure, Ultrasonic, Radar, etc.
    StandardCalibrationInterval INT, -- Days
    RequiresCertification BIT DEFAULT 0,
    RequiresFunctionalTest BIT DEFAULT 0,
    IsExplosionProof BIT DEFAULT 0,
    TypicalAccuracy NVARCHAR(50),
    TypicalRangeability NVARCHAR(50)
);
