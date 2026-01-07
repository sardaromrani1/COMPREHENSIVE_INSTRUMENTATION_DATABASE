-- 01_TABLE_InstrumentState.sql

/*==================================================================================================================
Table: InstrumentState
Layer: Lifecycle Model ( Layer2 )
Purpose:
	- Defines valid lifecycle states for instruments
	- Serves as reference for InstrumentLifecycle table
====================================================================================================================*/

CREATE TABLE InstrumentState(
	StateID INT IDENTITY(1, 1) PRIMARY KEY,
	StateCode NVARCHAR(50) NOT NULL UNIQUE,
	StateName NVARCHAR(100) NOT NULL,
	Description NVARCHAR(255),
	IsOperational BIT NOT NULL,
	IsActive BIT NOT NULL DEFAULT 1,
	CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO