-- ==========================================
-- 9. MAINTENANCE RECORDS - سوابق تعمیرات
-- ==========================================

CREATE TABLE MaintenanceRecords (
    MaintenanceID INT PRIMARY KEY IDENTITY(1,1),
    InstrumentID INT NOT NULL,
    
    -- Work Order
    WorkOrderNumber NVARCHAR(50) UNIQUE,
    WorkOrderType NVARCHAR(50), -- PM, CM, Breakdown, Overhaul, Modification
    
    -- Scheduling
    ScheduledDate DATE,
    RequestedDate DATE,
    StartDate DATETIME,
    CompletionDate DATETIME,
    
    -- Classification
    MaintenanceType NVARCHAR(50), -- Preventive, Corrective, Predictive, Breakdown
    MaintenanceCategory NVARCHAR(50), -- Inspection, Lubrication, Adjustment, Repair, Replacement
    Priority NVARCHAR(20), -- Routine, Medium, High, Emergency, Critical
    
    -- Personnel
    RequestedBy NVARCHAR(100),
    AssignedTo NVARCHAR(100),
    TechnicianID INT,
    SupervisorID INT,
    ContractorName NVARCHAR(100),
    
    -- Problem Description
    ProblemDescription NVARCHAR(2000),
    SymptomObserved NVARCHAR(1000),
    
    -- Root Cause Analysis
    RootCause NVARCHAR(1000),
    RootCauseCategory NVARCHAR(100), -- Design, Installation, Operation, Maintenance
    FailureMode NVARCHAR(200),
    
    -- Work Performed
    WorkPerformed NVARCHAR(2000),
    ActionTaken NVARCHAR(2000),
    PartsReplaced NVARCHAR(1000),
    
    -- Testing After Maintenance
    TestingPerformed NVARCHAR(1000),
    TestResults NVARCHAR(1000),
    CalibrationPerformed BIT DEFAULT 0,
    FunctionalTestPassed BIT DEFAULT 1,
    
    -- Downtime
    DowntimeStart DATETIME,
    DowntimeEnd DATETIME,
    DowntimeDuration_Hours AS (DATEDIFF(HOUR, DowntimeStart, DowntimeEnd)),
    PlannedDowntime BIT DEFAULT 1,
    ProductionImpact NVARCHAR(500),
    
    -- Cost
    LaborHours DECIMAL(10,2),
    LaborCost DECIMAL(18,2),
    PartsCost DECIMAL(18,2),
    ContractorCost DECIMAL(18,2),
    OtherCosts DECIMAL(18,2),
    TotalCost AS (ISNULL(LaborCost,0) + ISNULL(PartsCost,0) + ISNULL(ContractorCost,0) + ISNULL(OtherCosts,0)),
    
    -- Warranty
    IsWarrantyClaim BIT DEFAULT 0,
    WarrantyClaimNumber NVARCHAR(50),
    WarrantyApproved BIT,
    
    -- Status
    Status NVARCHAR(20) DEFAULT 'Completed',
    -- Requested, Scheduled, In Progress, On Hold, Completed, Cancelled
    
    -- Follow-up
    RequiresFollowUp BIT DEFAULT 0,
    FollowUpDate DATE,
    FollowUpAction NVARCHAR(1000),
    
    -- Recommendations
    Recommendations NVARCHAR(2000),
    PreventiveActions NVARCHAR(2000),
    
    -- Permits & Safety
    PermitRequired BIT DEFAULT 0,
    PermitNumber NVARCHAR(50),
    HotWorkPermit BIT DEFAULT 0,
    ConfinedSpacePermit BIT DEFAULT 0,
    
    -- Documentation
    AttachmentPath NVARCHAR(500),
    
    Notes NVARCHAR(MAX),
    
    FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
);
