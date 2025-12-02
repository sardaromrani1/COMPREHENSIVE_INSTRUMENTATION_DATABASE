-- 7. Triggers
-- Example: Log every new instrument added

CREATE TABLE InstrumentLog (
    LogID INT IDENTITY PRIMARY KEY,
    InstrumentID INT,
    ActionTaken VARCHAR(50),
    ActionDate DATETIME DEFAULT GETDATE()
);

GO

CREATE TRIGGER trg_InstrumentInsert
ON Instruments
AFTER INSERT
AS
BEGIN
    INSERT INTO InstrumentLog (InstrumentID, ActionTaken)
    SELECT InstrumentID, 'Inserted'
    FROM inserted;
END;
