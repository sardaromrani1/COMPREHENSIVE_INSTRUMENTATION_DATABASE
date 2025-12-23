-- INSERT INTO InstrumentStatus

INSERT INTO InstrumentStatus VALUES
('INSTALLED', 'Installed but not commissioned'),
('INSERVICE', 'Operational'),
('OUTOFSERVICE', 'Temporarily unavailable'),
('DECOMMISSIONED', 'Permanently removed');

-- 'Statuses are normalized to avoid free-text inconsistencies'