-- 5. MERGE (Upsert operation)

-- Goal: Update instrument info if exists, otherwise insert a new instrument.

MERGE INTO Instruments AS target
USING (VALUES 
    (101, 'PT-1005', 2, 3, 1, 5)
) AS src (InstrumentID, InstrumentTag, TypeID, SiteID, SubSystemID, ManufacturerID)
ON target.InstrumentID = src.InstrumentID

WHEN MATCHED THEN
    UPDATE SET 
        target.TagNumber = src.InstrumentTag,
        target.InstrumentTypeID = src.TypeID

WHEN NOT MATCHED THEN
    INSERT (InstrumentID, TagNumber, InstrumentTypeID, SiteID, SubSystemID, ManufacturerID)
    VALUES (src.InstrumentID, src.InstrumentTag, src.TypeID, src.SiteID, src.SubSystemID, src.ManufacturerID);
