-- Fact Table

CREATE TABLE InstrumentCost(
	InstrumentCostID BIGINT IDENTITY(1, 1) PRIMARY KEY,
	InstrumentID INT NOT NULL,
	CostTypeID INT NOT NULL,
	CostAmount DECIMAL(18, 2) NOT NULL,
	CostDate DATE NOT NULL,
	RelatedMaintenanceID INT NULL,
	Notes NVARCHAR(255),
	CONSTRAINT FK_InstrumentCost_CostType
		FOREIGN KEY (CostTypeID)
		REFERENCES CostType(CostTypeID)
);