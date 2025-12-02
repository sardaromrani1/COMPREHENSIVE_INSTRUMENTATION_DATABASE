-- 5. Find gaps between installations (LAG Example)

-- If you want to track installation activity over time.

SELECT
    InstrumentID,
    TagNumber,
    InstallationDate,
    LAG(InstallationDate) OVER (ORDER BY InstallationDate) AS PreviousInstall,
    DATEDIFF(day, 
        LAG(InstallationDate) OVER (ORDER BY InstallationDate), 
        InstallationDate) AS DaysBetweenInstalls
FROM Instruments;
