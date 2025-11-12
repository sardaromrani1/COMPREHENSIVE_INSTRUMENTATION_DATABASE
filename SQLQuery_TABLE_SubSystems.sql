-- Sub-Systems within Units
CREATE TABLE SubSystems (
    SubSystemID INT PRIMARY KEY IDENTITY(1,1),
    UnitID INT NOT NULL,
    SubSystemCode NVARCHAR(20) UNIQUE NOT NULL,
    SubSystemName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    FOREIGN KEY (UnitID) REFERENCES ProcessUnits(UnitID)
);
