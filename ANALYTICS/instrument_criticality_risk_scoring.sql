-- Criticality & Risk Scoring (combine multi-factors)
-- Create a type-weight mapping (inline) and compute score

-- adjust weights per your engineering judgement
WITH type_weights AS (
  SELECT InstrumentTypeID, TypeName,
    CASE 
      WHEN TypeName LIKE '%Pressure%' THEN 5
      WHEN TypeName LIKE '%Level%' THEN 4
      WHEN TypeName LIKE '%Flow%' THEN 4
      WHEN TypeName LIKE '%Temperature%' THEN 3
      ELSE 2
    END AS TypeWeight
  FROM InstrumentTypes
),
instr AS (
  SELECT i.InstrumentID, i.TagNumber, i.InstrumentTypeID, i.InstallationDate, i.SubSystemID,
         CASE WHEN t.InstrumentTypeID IS NULL THEN 1 ELSE t.TypeWeight END AS TypeWeight,
         CASE WHEN ti.InstrumentID IS NOT NULL THEN 1 ELSE 0 END AS IsTripInstrument,
         DATEDIFF(day, i.InstallationDate, GETDATE())/365.0 AS AgeYears
  FROM Instruments i
  LEFT JOIN type_weights t ON i.InstrumentTypeID = t.InstrumentTypeID
  LEFT JOIN TripInstruments ti ON i.InstrumentID = ti.InstrumentID
)
SELECT
  InstrumentID, TagNumber, SubSystemID, TypeWeight, IsTripInstrument, AgeYears,
  -- simple linear score: weight*2 + trip_flag*5 + age factor
  (TypeWeight * 2.0) + (IsTripInstrument * 5.0) + (CASE WHEN AgeYears > 5 THEN 3 ELSE AgeYears END) AS CriticalityScore
FROM instr
ORDER BY CriticalityScore DESC;
