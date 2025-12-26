-- Cost Taxonomy table

CREATE TABLE CostType(
	CostTypeID INT IDENTITY(1, 1) PRIMARY KEY,
	CostCategory NVARCHAR(50) NOT NULL,	-- CAPEX, OPEX
	CostSubCategory NVARCHAR(50) NOT NULL,	-- Maintenance, Spare, Calibration, Downtime, Energy
	Description NVARCHAR(255)
);