
CREATE TABLE SpareParts (
    SparePartID INT PRIMARY KEY IDENTITY(1,1),
    
    -- Identification
    PartNumber NVARCHAR(100) UNIQUE NOT NULL,
    ManufacturerPartNumber NVARCHAR(100),
    AlternatePartNumber NVARCHAR(100),
    PartName NVARCHAR(200) NOT NULL,
    Description NVARCHAR(1000),
    
    -- Classification
    PartCategory NVARCHAR(50), -- Sensor, Transmitter, Electronics, Housing, Gasket, Diaphragm, etc.
    PartSubCategory NVARCHAR(50), -- Pressure Sensor, Temperature Element, Circuit Board, etc.
    PartType NVARCHAR(50), -- Consumable, Repairable, Critical, Insurance
    
    -- Manufacturer Information
    ManufacturerID INT,
    ManufacturerName NVARCHAR(100), -- Denormalized for quick access
    
    -- Compatibility
    InstrumentTypeID INT,
    CompatibleModels NVARCHAR(500), -- Comma-separated list of models
    CompatibleTags NVARCHAR(1000), -- List of instrument tags that use this part
    Interchangeable BIT DEFAULT 0, -- Can be replaced with alternatives
    InterchangeableWith NVARCHAR(500), -- List of alternative part numbers
    
    -- Technical Specifications
    TechnicalSpecs NVARCHAR(2000),
    Material NVARCHAR(200),
    Dimensions NVARCHAR(200), -- Length x Width x Height
    Weight_Kg DECIMAL(10,3),
    
    -- Procurement
    UnitOfMeasure NVARCHAR(20), -- Each, Set, Meter, Liter, etc.
    UnitCost DECIMAL(18,2),
    Currency NVARCHAR(10) DEFAULT 'USD',
    LastPurchasePrice DECIMAL(18,2),
    LastPurchaseDate DATE,
    PriceValidUntil DATE,
    
    -- Suppliers (Primary and Alternatives)
    PrimarySupplier NVARCHAR(100),
    PrimarySupplierContact NVARCHAR(100),
    AlternativeSupplier1 NVARCHAR(100),
    AlternativeSupplier2 NVARCHAR(100),
    
    -- Lead Time
    LeadTime_Days INT,
    LeadTimeCategory NVARCHAR(20), -- Stock, Short, Medium, Long, Critical
    EmergencyProcurement BIT DEFAULT 0,
    EmergencySupplier NVARCHAR(100),
    
    -- Inventory Management
    MinStockLevel INT DEFAULT 0,
    MaxStockLevel INT,
    ReorderPoint INT,
    ReorderQuantity INT,
    SafetyStock INT DEFAULT 0,
    EconomicOrderQuantity INT, -- EOQ
    
    -- Usage Statistics
    AnnualUsage INT DEFAULT 0,
    AverageMonthlyUsage DECIMAL(10,2) DEFAULT 0,
    LastUsedDate DATE,
    UsageFrequency NVARCHAR(20), -- Daily, Weekly, Monthly, Quarterly, Rarely
    
    -- Criticality
    Criticality NVARCHAR(20) DEFAULT 'Medium', -- Low, Medium, High, Critical
    IsInsuranceSpare BIT DEFAULT 0, -- Must always be in stock
    IsCriticalSpare BIT DEFAULT 0,
    IsLongLeadItem BIT DEFAULT 0,
    
    -- Shelf Life
    HasShelfLife BIT DEFAULT 0,
    ShelfLife_Months INT,
    RequiresSpecialStorage BIT DEFAULT 0,
    StorageConditions NVARCHAR(500), -- Temperature, Humidity, etc.
    
    -- Quality & Certification
    RequiresCertification BIT DEFAULT 0,
    CertificationType NVARCHAR(100), -- Material Test Report, Calibration Certificate
    QualityStandard NVARCHAR(100), -- ISO, API, ASTM, etc.
    
    -- Obsolescence
    IsObsolete BIT DEFAULT 0,
    ObsolescenceDate DATE,
    ObsolescenceReason NVARCHAR(500),
    ReplacementPartNumber NVARCHAR(100),
    
    -- Warranty
    WarrantyPeriod_Months INT,
    WarrantyTerms NVARCHAR(500),
    
    -- Documentation
    DatasheetPath NVARCHAR(500),
    DrawingPath NVARCHAR(500),
    ImagePath NVARCHAR(500),
    CertificatePath NVARCHAR(500),
    
    -- HSE Information
    IsHazardousMaterial BIT DEFAULT 0,
    MSDS_Path NVARCHAR(500), -- Material Safety Data Sheet
    HandlingInstructions NVARCHAR(1000),
    DisposalRequirements NVARCHAR(500),
    
    -- Tracking
    CreatedBy NVARCHAR(100),
    CreatedDate DATETIME DEFAULT GETDATE(),
    ModifiedBy NVARCHAR(100),
    ModifiedDate DATETIME,
    LastReviewDate DATE,
    NextReviewDate DATE,
    
    -- Status
    IsActive BIT DEFAULT 1,
    IsApproved BIT DEFAULT 0,
    ApprovedBy NVARCHAR(100),
    ApprovalDate DATE,
    
    Notes NVARCHAR(MAX),
    
    -- Foreign Keys
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
    FOREIGN KEY (InstrumentTypeID) REFERENCES InstrumentTypes(InstrumentTypeID)
);

-- Indexes for SpareParts
CREATE NONCLUSTERED INDEX IX_SpareParts_PartNumber 
    ON SpareParts(PartNumber) INCLUDE (PartName, PartCategory);

CREATE NONCLUSTERED INDEX IX_SpareParts_Category 
    ON SpareParts(PartCategory, PartSubCategory);

CREATE NONCLUSTERED INDEX IX_SpareParts_Manufacturer 
    ON SpareParts(ManufacturerID) INCLUDE (ManufacturerPartNumber);

CREATE NONCLUSTERED INDEX IX_SpareParts_Criticality 
    ON SpareParts(Criticality, IsCriticalSpare);

CREATE NONCLUSTERED INDEX IX_SpareParts_InstrumentType 
    ON SpareParts(InstrumentTypeID);

GO
