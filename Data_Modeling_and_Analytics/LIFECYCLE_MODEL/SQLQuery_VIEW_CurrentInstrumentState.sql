-- 03_VIEW_CurrentInstrumentState.sql

/*===================================================================================================================
View: VIEW_CurrentInstrumentState
Layer: Lifecycle Model (Layer 2)
Purpose:
	- Returns the current lifecycle state of each instrument
====================================================================================================================*/

CREATE OR ALTER VIEW VIEW_CurrentInstrumentState AS 
SELECT
	il.InstrumentID,
	il.StateID,
	s.StateCode,
	s.StateName,
	il.StateStartTime,
	il.ChangeReason

FROM InstrumentLifecycle il
INNER JOIN InstrumentState s
	ON il.StateID = s.StateID
WHERE il.StateEndTime IS NULL;
GO