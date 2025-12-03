--  Operational Reports & Automation
--  Stored procedure to return top N critical instruments (example)

CREATE PROCEDURE dbo.sp_GetTopCriticalInstruments
  @TopN INT = 50
AS
BEGIN
  SET NOCOUNT ON;

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
    SELECT i.InstrumentID, i.TagNumber, i.SubSystemID, i.InstallationDate,
      COALESCE(t.TypeWeight,1) AS TypeWeight,
      CASE WHEN ti.InstrumentID IS NOT NULL THEN 1 ELSE 0 END AS IsTrip,
      (COALESCE(t.TypeWeight,1)*2) + (CASE WHEN ti.InstrumentID IS NOT NULL THEN 5 ELSE 0 END) + (DATEDIFF(day, i.InstallationDate, GETDATE())/365.0) AS CriticalityScore
    FROM Instruments i
    LEFT JOIN type_weights t ON i.InstrumentTypeID = t.InstrumentTypeID
    LEFT JOIN TripInstruments ti ON i.InstrumentID = ti.InstrumentID
  )
  SELECT TOP (@TopN) *
  FROM score
  ORDER BY CriticalityScore DESC;
END;
GO
