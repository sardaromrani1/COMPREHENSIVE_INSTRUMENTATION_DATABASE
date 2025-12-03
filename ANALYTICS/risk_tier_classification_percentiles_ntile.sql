-- Percentiles & Bucketing (NTILE)
-- Bucket instruments into 4 risk tiers by criticality score (NTILE)

-- reuse criticality calculation as inline CTE
WITH type_weights AS (
  SELECT InstrumentTypeID, TypeName,
    CASE WHEN TypeName LIKE '%Pressure%' THEN 5
         WHEN TypeName LIKE '%Flow%' THEN 4
         WHEN TypeName LIKE '%Level%' THEN 4
         WHEN TypeName LIKE '%Temperature%' THEN 3
         ELSE 2 END AS TypeWeight
  FROM InstrumentTypes
),
score AS (
  SELECT i.InstrumentID, i.TagNumber, i.InstrumentTypeID, i.InstallationDate,
    COALESCE(t.TypeWeight, 1) AS TypeWeight,
    CASE WHEN ti.InstrumentID IS NOT NULL THEN 1 ELSE 0 END AS IsTrip,
    (COALESCE(t.TypeWeight,1)*2) + (CASE WHEN ti.InstrumentID IS NOT NULL THEN 5 ELSE 0 END) + (DATEDIFF(day, i.InstallationDate, GETDATE())/365.0) AS Score
  FROM Instruments i
  LEFT JOIN type_weights t ON i.InstrumentTypeID = t.InstrumentTypeID
  LEFT JOIN TripInstruments ti ON i.InstrumentID = ti.InstrumentID
)
SELECT *,
  NTILE(4) OVER (ORDER BY Score DESC) AS RiskTier -- 1 highest? depends on ORDER
FROM score
ORDER BY Score DESC;
