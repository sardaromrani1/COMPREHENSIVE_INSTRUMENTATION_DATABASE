INSERT INTO EventType( EventTypeCode, EventTypeName, Description )
VALUES(
('FAILURE', 'Failure Event', 'Instrument failure or malfunction'),
('MAINTENANCE', 'Maintenance Event', 'Maintenance or repair activity'),
('ALARM', 'Alarm Event', 'Alarm raised by instrument'),
('TRIP', 'Trip Event', 'Protective trip activation'),
('CALIBRATION', 'Calibration Event', 'Calibration activity')
);
GO