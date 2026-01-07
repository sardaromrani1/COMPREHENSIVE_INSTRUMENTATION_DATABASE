SELECT
	a.AlarmEventID,
	a.EventTime	AS AlarmTime,

	t.TripEventID,
	t.EventTime AS TripTime,

	f.FailureEventID,
	f.FailureStartTime,

	m.MaintenanceEventID,
	m.MaintenanceEndTime

FROM AlarmEvent a
LEFT JOIN AlarmFailureLink af
	ON a.AlarmEventID = af.AlarmEventID

LEFT JOIN FailureEvent f
	ON af.FailureEventID = f.FailureEventID

LEFT JOIN TripFailureLink tf
	ON f.FailureEventID = tf.FailureEventID

LEFT JOIN TripEvent t
	ON tf.TripEventID = t.TripEventID

LEFT JOIN FailureMaintenanceLink fm
	ON f.FailureEventID = fm.FailureEventID

LEFT JOIN MaintenanceEvent m
	ON fm.MaintenanceEventID = m.MaintenanceEventID

