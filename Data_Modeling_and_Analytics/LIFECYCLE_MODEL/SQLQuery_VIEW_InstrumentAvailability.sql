-- 04_VIEW_InstrumentAvailability.sql

/*===================================================================================================================
View: VIEW_InstrumentAvailability
Layer: Lifecycle Model (Layer 2)
Purpose:
	- Calculates uptime, downtime, and availability per instrument
====================================================================================================================*/

CREATE OR ALTER VIEW VIEW_InstrumentAvailability AS
	WITH LifecycleDurations AS(
		SELECT
			il.InstrumentID,
			s.IsOperational,
			DATEDIFF(
				SECOND,
				il.StateStartTime,
				ISNULL(il.StateEndTime, SYSDATETIME())
			) AS DurationSeconds
		FROM InstrumentLifecycle il
		INNER JOIN InstrumentState s
			ON il.StateID = s.StateID
)

SELECT
	InstrumentID,
	SUM( CASE WHEN IsOperational = 1 THEN DurationSeconds ELSE 0 END ) AS UptimeSeconds,
	SUM( CASE WHEN IsOperational = 0 THEN DurationSeconds ELSE 0 END ) AS DowntimeSeconds,
	CAST(
		100.0 *
		SUM( CASE WHEN IsOperational = 1 THEN DurationSeconds ELSE 0 END ) / NULLIF( SUM (DurationSeconds), 0) AS DECIMAL(5, 2)) AS AvailabilityPercent 
FROM LifecycleDurations
GROUP BY InstrumentID;
GO
