ALTER TABLE FailureRecords
ADD CONSTRAINT FK_FailureRecords_Severity
FOREIGN KEY (SeverityID)
REFERENCES Severity (SeverityID);