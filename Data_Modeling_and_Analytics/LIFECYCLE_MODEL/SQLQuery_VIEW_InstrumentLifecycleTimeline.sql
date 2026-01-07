-- 04_VIEW_InstrumentLifecycleTimeline.sql

/*====================================================================================================================
View: VIEW_InstrumentLifecycleTimeline
Layer: Lifecycle Model (Layer 2)
Purpose:
	- Provides full lifecycle timeline per instrument
	- Used for diagnostics, RCA, and time-based analysis
=====================================================================================================================*/

CREATE OR ALTER VIEW dbo.VIEW_InstrumentLifecycleTimeline
AS
SELECT
    il.InstrumentID,
    i.TagNumber,
    i.Description AS InstrumentDescription,
    il.LifecycleID,
    s.StateCode,
    s.StateName,
    il.StateStartTime,
    il.StateEndTime,
    DATEDIFF(
        SECOND,
        il.StateStartTime,
        ISNULL(il.StateEndTime, SYSDATETIME())
    ) AS DurationSeconds,
    s.IsOperational,
    il.ChangeReason,
    il.SourceEventType
FROM dbo.InstrumentLifecycle AS il
INNER JOIN dbo.InstrumentState AS s
    ON il.StateID = s.StateID
INNER JOIN dbo.Instruments AS i
    ON il.InstrumentID = i.InstrumentID;
GO
