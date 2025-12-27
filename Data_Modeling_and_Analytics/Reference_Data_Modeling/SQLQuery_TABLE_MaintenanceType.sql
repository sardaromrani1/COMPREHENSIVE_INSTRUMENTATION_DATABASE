CREATE TABLE MaintenanceType(
	MaintenanceTypeID INT IDENTITY(1, 1) PRIMARY KEY,
	MaintenanceTypeCode NVARCHAR(50) NOT NULL UNIQUE,
	Description NVARCHAR(255)
);