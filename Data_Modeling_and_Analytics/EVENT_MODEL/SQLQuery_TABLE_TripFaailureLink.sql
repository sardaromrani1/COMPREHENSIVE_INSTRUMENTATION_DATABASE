CREATE TABLE TripFailureLink(
    TripEventID BIGINT NOT NULL,
    FailureEventID INT NOT NULL,

    CONSTRAINT PK_TripFailureLink
        PRIMARY KEY (TripEventID, FailureEventID),

    CONSTRAINT FK_TripFailureLink_TripEvent
        FOREIGN KEY (TripEventID)
        REFERENCES TripEvent(TripEventID),

    CONSTRAINT FK_TripFailureLink_FailureEvent
        FOREIGN KEY (FailureEventID)
        REFERENCES FailureEvent(FailureEventID)
);
