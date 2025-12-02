CREATE TABLE SparePartUsage (
    UsageID INT IDENTITY(1,1) PRIMARY KEY,
    SparePartID INT NOT NULL,
    Quantity INT NOT NULL,                   -- number of pieces used
    UsageDate DATE NOT NULL,                 -- when the part was consumed
    WorkOrderNumber NVARCHAR(50),            -- optional: link to maintenance
    MaintenanceID INT,                       -- optional: FK to MaintenanceRecords
    Notes NVARCHAR(500),

    FOREIGN KEY (SparePartID) REFERENCES SpareParts(SparePartID),
    FOREIGN KEY (MaintenanceID) REFERENCES MaintenanceRecords(MaintenanceID)
);
