CREATE TABLE AlarmFailureLink(
    AlarmEventID BIGINT NOT NULL,
    FailureEventID INT NOT NULL,
    CreatedAt DATETIME2 NOT NULL 
        CONSTRAINT DF_AlarmFailureLink_CreatedAt DEFAULT SYSDATETIME(),

    CONSTRAINT PK_AlarmFailureLink
        PRIMARY KEY (AlarmEventID, FailureEventID),

    CONSTRAINT FK_AlarmFailureLink_AlarmEvent
        FOREIGN KEY (AlarmEventID)
        REFERENCES AlarmEvent(AlarmEventID),

    CONSTRAINT FK_AlarmFailureLink_FailureEvent
        FOREIGN KEY (FailureEventID)
        REFERENCES FailureEvent(FailureEventID)
);
