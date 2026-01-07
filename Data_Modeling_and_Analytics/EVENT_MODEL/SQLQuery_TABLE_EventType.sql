-- 01_TABLE_EventType.sql
/*===================================================================================================================
Table: EventType
Layer: Event Model (Layer 3)
Purpose:
	- Defines high-level types of asset-related events
===================================================================================================================*/

CREATE TABLE EventType(
	EventTypeID INT IDENTITY(1, 1) PRIMARY KEY,
	EventTypeCode NVARCHAR(50) NOT NULL UNIQUE,
	EventTypeName NVARCHAR(100) NOT NULL,
	Description NVARCHAR(255),
	IsActive BIT NOT NULL DEFAULT 1,
	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);