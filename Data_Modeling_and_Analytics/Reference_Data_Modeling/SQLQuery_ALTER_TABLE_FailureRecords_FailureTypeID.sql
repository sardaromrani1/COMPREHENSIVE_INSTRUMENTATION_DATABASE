ALTER TABLE FailureRecords
ADD CONSTRAINT FK_FailureRecords_FailureType
FOREIGN KEY (FailureTypeID)
REFERENCES FailureType (FailureTypeID);