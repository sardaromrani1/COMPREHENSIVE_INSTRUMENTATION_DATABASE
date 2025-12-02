-- 6. User-Defined Functions (UDF)
-- Inline Table Function

-- Goal: Return all instruments for a given manufacturer.

CREATE FUNCTION uf_GetInstrumentsByManufacturer(@ManufacturerID INT)
RETURNS TABLE
AS
RETURN
(
    SELECT InstrumentID, TagNumber
    FROM Instruments
    WHERE ManufacturerID = @ManufacturerID
);

-- Then call it:

-- SELECT * FROM uf_GetInstrumentsByManufacturer(3);

