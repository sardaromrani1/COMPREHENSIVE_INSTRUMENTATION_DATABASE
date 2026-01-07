-- NOTE:
-- 1. InstrumentID must exist in dbo.Instruments (FK constraint).
-- 2. EventTypeID must exist in dbo.EventType (FK constraint).


INSERT INTO AssetEvent
(InstrumentID, EventTypeID, EventStartTime, Severity, Description)
VALUES
(101, 1, '2024-03-15 10:30', 'HIGH', 'Pressure Transmitter Failure')
;