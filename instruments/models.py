# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Alarmconfiguration(models.Model):
    alarmid = models.AutoField(db_column='AlarmID', primary_key=True)  # Field name made lowercase.
    instrumentid = models.ForeignKey('Instruments', models.DO_NOTHING, db_column='InstrumentID')  # Field name made lowercase.
    alarmtype = models.CharField(db_column='AlarmType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alarmdescription = models.CharField(db_column='AlarmDescription', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alarmsetpoint = models.DecimalField(db_column='AlarmSetpoint', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    alarmdeadband = models.DecimalField(db_column='AlarmDeadband', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    alarmdelay_seconds = models.IntegerField(db_column='AlarmDelay_Seconds', blank=True, null=True)  # Field name made lowercase.
    alarmpriority = models.CharField(db_column='AlarmPriority', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alarmaction = models.CharField(db_column='AlarmAction', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    requiresacknowledgement = models.BooleanField(db_column='RequiresAcknowledgement', blank=True, null=True)  # Field name made lowercase.
    isenabled = models.BooleanField(db_column='IsEnabled', blank=True, null=True)  # Field name made lowercase.
    enableddate = models.DateField(db_column='EnabledDate', blank=True, null=True)  # Field name made lowercase.
    disableddate = models.DateField(db_column='DisabledDate', blank=True, null=True)  # Field name made lowercase.
    disabledby = models.CharField(db_column='DisabledBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    disabledreason = models.CharField(db_column='DisabledReason', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AlarmConfiguration'


class Calibrationrecords(models.Model):
    calibrationid = models.AutoField(db_column='CalibrationID', primary_key=True)  # Field name made lowercase.
    instrumentid = models.ForeignKey('Instruments', models.DO_NOTHING, db_column='InstrumentID')  # Field name made lowercase.
    scheduleddate = models.DateField(db_column='ScheduledDate', blank=True, null=True)  # Field name made lowercase.
    actualdate = models.DateTimeField(db_column='ActualDate')  # Field name made lowercase.
    nextduedate = models.DateField(db_column='NextDueDate', blank=True, null=True)  # Field name made lowercase.
    calibratedby = models.CharField(db_column='CalibratedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    technicianid = models.IntegerField(db_column='TechnicianID', blank=True, null=True)  # Field name made lowercase.
    supervisedby = models.CharField(db_column='SupervisedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    witnessedby = models.CharField(db_column='WitnessedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    calibrationmethod = models.CharField(db_column='CalibrationMethod', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    calibrationprocedure = models.CharField(db_column='CalibrationProcedure', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    referencestandard = models.CharField(db_column='ReferenceStandard', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    referenceequipmentid = models.IntegerField(db_column='ReferenceEquipmentID', blank=True, null=True)  # Field name made lowercase.
    referenceequipmenttag = models.CharField(db_column='ReferenceEquipmentTag', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    referenceaccuracy = models.CharField(db_column='ReferenceAccuracy', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    traceabilitycertificate = models.CharField(db_column='TraceabilityCertificate', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ambienttemperature = models.DecimalField(db_column='AmbientTemperature', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ambienthumidity = models.DecimalField(db_column='AmbientHumidity', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ambientpressure = models.DecimalField(db_column='AmbientPressure', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    testpointscount = models.IntegerField(db_column='TestPointsCount', blank=True, null=True)  # Field name made lowercase.
    passedpoints = models.IntegerField(db_column='PassedPoints', blank=True, null=True)  # Field name made lowercase.
    failedpoints = models.IntegerField(db_column='FailedPoints', blank=True, null=True)  # Field name made lowercase.
    asfoundcondition = models.CharField(db_column='AsFoundCondition', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    asfoundmaxerror = models.DecimalField(db_column='AsFoundMaxError', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asfoundmaxerror_percent = models.DecimalField(db_column='AsFoundMaxError_Percent', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    asleftcondition = models.CharField(db_column='AsLeftCondition', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    asleftmaxerror = models.DecimalField(db_column='AsLeftMaxError', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asleftmaxerror_percent = models.DecimalField(db_column='AsLeftMaxError_Percent', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    adjustmentrequired = models.BooleanField(db_column='AdjustmentRequired', blank=True, null=True)  # Field name made lowercase.
    adjustmentmade = models.CharField(db_column='AdjustmentMade', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    acceptancecriteria = models.CharField(db_column='AcceptanceCriteria', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    measurementuncertainty = models.CharField(db_column='MeasurementUncertainty', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    calibrationresult = models.CharField(db_column='CalibrationResult', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    certificatenumber = models.CharField(db_column='CertificateNumber', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    certificatepath = models.CharField(db_column='CertificatePath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isaccreditedcalibration = models.BooleanField(db_column='IsAccreditedCalibration', blank=True, null=True)  # Field name made lowercase.
    accreditationbody = models.CharField(db_column='AccreditationBody', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='StartTime', blank=True, null=True)  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='EndTime', blank=True, null=True)  # Field name made lowercase.
    duration_minutes = models.IntegerField(db_column='Duration_Minutes', blank=True, null=True)  # Field name made lowercase.
    laborcost = models.DecimalField(db_column='LaborCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    materialcost = models.DecimalField(db_column='MaterialCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalcost = models.DecimalField(db_column='TotalCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    issuesfound = models.CharField(db_column='IssuesFound', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    correctiveactions = models.CharField(db_column='CorrectiveActions', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    followuprequired = models.BooleanField(db_column='FollowUpRequired', blank=True, null=True)  # Field name made lowercase.
    followupdate = models.DateField(db_column='FollowUpDate', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CalibrationRecords'


class Calibrationtestpoints(models.Model):
    testpointid = models.AutoField(db_column='TestPointID', primary_key=True)  # Field name made lowercase.
    calibrationid = models.ForeignKey(Calibrationrecords, models.DO_NOTHING, db_column='CalibrationID')  # Field name made lowercase.
    testsequence = models.IntegerField(db_column='TestSequence', blank=True, null=True)  # Field name made lowercase.
    appliedinput = models.DecimalField(db_column='AppliedInput', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asfoundoutput = models.DecimalField(db_column='AsFoundOutput', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asleftoutput = models.DecimalField(db_column='AsLeftOutput', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expectedoutput = models.DecimalField(db_column='ExpectedOutput', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asfounderror = models.DecimalField(db_column='AsFoundError', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    asfounderror_percent = models.DecimalField(db_column='AsFoundError_Percent', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    aslefterror = models.DecimalField(db_column='AsLeftError', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    aslefterror_percent = models.DecimalField(db_column='AsLeftError_Percent', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iswithintolerance = models.BooleanField(db_column='IsWithinTolerance', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CalibrationTestPoints'


class Controlsystems(models.Model):
    systemid = models.AutoField(db_column='SystemID', primary_key=True)  # Field name made lowercase.
    unitid = models.ForeignKey('Processunits', models.DO_NOTHING, db_column='UnitID', blank=True, null=True)  # Field name made lowercase.
    systemcode = models.CharField(db_column='SystemCode', unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    systemname = models.CharField(db_column='SystemName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    systemtype = models.CharField(db_column='SystemType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    manufacturer = models.CharField(db_column='Manufacturer', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    model = models.CharField(db_column='Model', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    softwareversion = models.CharField(db_column='SoftwareVersion', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    firmwareversion = models.CharField(db_column='FirmwareVersion', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    installdate = models.DateField(db_column='InstallDate', blank=True, null=True)  # Field name made lowercase.
    commissiondate = models.DateField(db_column='CommissionDate', blank=True, null=True)  # Field name made lowercase.
    lastupgradedate = models.DateField(db_column='LastUpgradeDate', blank=True, null=True)  # Field name made lowercase.
    redundancylevel = models.CharField(db_column='RedundancyLevel', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    communicationprotocol = models.CharField(db_column='CommunicationProtocol', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    maintenancecontract = models.CharField(db_column='MaintenanceContract', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contractexpirydate = models.DateField(db_column='ContractExpiryDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ControlSystems'


class Failurerecords(models.Model):
    failureid = models.AutoField(db_column='FailureID', primary_key=True)  # Field name made lowercase.
    instrumentid = models.ForeignKey('Instruments', models.DO_NOTHING, db_column='InstrumentID')  # Field name made lowercase.
    maintenanceid = models.ForeignKey('Maintenancerecords', models.DO_NOTHING, db_column='MaintenanceID', blank=True, null=True)  # Field name made lowercase.
    failuredate = models.DateTimeField(db_column='FailureDate')  # Field name made lowercase.
    detecteddate = models.DateTimeField(db_column='DetectedDate', blank=True, null=True)  # Field name made lowercase.
    reporteddate = models.DateTimeField(db_column='ReportedDate', blank=True, null=True)  # Field name made lowercase.
    detectedby = models.CharField(db_column='DetectedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    detectionmethod = models.CharField(db_column='DetectionMethod', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    failuremode = models.CharField(db_column='FailureMode', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    failuretype = models.CharField(db_column='FailureType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    failuremechanism = models.CharField(db_column='FailureMechanism', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    failurecause = models.CharField(db_column='FailureCause', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rootcause = models.CharField(db_column='RootCause', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    severity = models.CharField(db_column='Severity', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    safetyimpact = models.CharField(db_column='SafetyImpact', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    productionimpact = models.CharField(db_column='ProductionImpact', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    environmentalimpact = models.CharField(db_column='EnvironmentalImpact', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    financialimpact = models.DecimalField(db_column='FinancialImpact', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    immediateaction = models.CharField(db_column='ImmediateAction', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    bypassimplemented = models.BooleanField(db_column='BypassImplemented', blank=True, null=True)  # Field name made lowercase.
    redundantinstrumentactivated = models.BooleanField(db_column='RedundantInstrumentActivated', blank=True, null=True)  # Field name made lowercase.
    emergencyshutdowntriggered = models.BooleanField(db_column='EmergencyShutdownTriggered', blank=True, null=True)  # Field name made lowercase.
    resolutiondate = models.DateTimeField(db_column='ResolutionDate', blank=True, null=True)  # Field name made lowercase.
    resolutiondescription = models.CharField(db_column='ResolutionDescription', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mttr_hours = models.IntegerField(db_column='MTTR_Hours', blank=True, null=True)  # Field name made lowercase.
    isrepeatfailure = models.BooleanField(db_column='IsRepeatFailure', blank=True, null=True)  # Field name made lowercase.
    previousfailureid = models.ForeignKey('self', models.DO_NOTHING, db_column='PreviousFailureID', blank=True, null=True)  # Field name made lowercase.
    repeatfailurecount = models.IntegerField(db_column='RepeatFailureCount', blank=True, null=True)  # Field name made lowercase.
    timesincepreviousfailure_days = models.IntegerField(db_column='TimeSincePreviousFailure_Days', blank=True, null=True)  # Field name made lowercase.
    repaircost = models.DecimalField(db_column='RepairCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    productionlosscost = models.DecimalField(db_column='ProductionLossCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalcost = models.DecimalField(db_column='TotalCost', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    preventiveaction = models.CharField(db_column='PreventiveAction', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    designmodificationrequired = models.BooleanField(db_column='DesignModificationRequired', blank=True, null=True)  # Field name made lowercase.
    procedureupdaterequired = models.BooleanField(db_column='ProcedureUpdateRequired', blank=True, null=True)  # Field name made lowercase.
    trainingrequired = models.BooleanField(db_column='TrainingRequired', blank=True, null=True)  # Field name made lowercase.
    investigationrequired = models.BooleanField(db_column='InvestigationRequired', blank=True, null=True)  # Field name made lowercase.
    investigationcompleted = models.BooleanField(db_column='InvestigationCompleted', blank=True, null=True)  # Field name made lowercase.
    investigationreport = models.CharField(db_column='InvestigationReport', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FailureRecords'


class Instrumentdetails(models.Model):
    instrumentid = models.IntegerField(db_column='InstrumentID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'InstrumentDetails'


class Instrumenttypes(models.Model):
    instrumenttypeid = models.AutoField(db_column='InstrumentTypeID', primary_key=True)  # Field name made lowercase.
    typecode = models.CharField(db_column='TypeCode', unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    typename = models.CharField(db_column='TypeName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    subcategory = models.CharField(db_column='SubCategory', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    measurementprinciple = models.CharField(db_column='MeasurementPrinciple', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    standardcalibrationinterval = models.IntegerField(db_column='StandardCalibrationInterval', blank=True, null=True)  # Field name made lowercase.
    requirescertification = models.BooleanField(db_column='RequiresCertification', blank=True, null=True)  # Field name made lowercase.
    requiresfunctionaltest = models.BooleanField(db_column='RequiresFunctionalTest', blank=True, null=True)  # Field name made lowercase.
    isexplosionproof = models.BooleanField(db_column='IsExplosionProof', blank=True, null=True)  # Field name made lowercase.
    typicalaccuracy = models.CharField(db_column='TypicalAccuracy', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    typicalrangeability = models.CharField(db_column='TypicalRangeability', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'InstrumentTypes'


class Instruments(models.Model):
    instrumentid = models.AutoField(db_column='InstrumentID', primary_key=True)  # Field name made lowercase.
    tagnumber = models.CharField(db_column='TagNumber', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    alternatetag = models.CharField(db_column='AlternateTag', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    serialnumber = models.CharField(db_column='SerialNumber', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    assetnumber = models.CharField(db_column='AssetNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    siteid = models.ForeignKey('Sites', models.DO_NOTHING, db_column='SiteID')  # Field name made lowercase.
    unitid = models.ForeignKey('Processunits', models.DO_NOTHING, db_column='UnitID')  # Field name made lowercase.
    subsystemid = models.ForeignKey('Subsystems', models.DO_NOTHING, db_column='SubSystemID', blank=True, null=True)  # Field name made lowercase.
    systemid = models.ForeignKey(Controlsystems, models.DO_NOTHING, db_column='SystemID', blank=True, null=True)  # Field name made lowercase.
    instrumenttypeid = models.ForeignKey(Instrumenttypes, models.DO_NOTHING, db_column='InstrumentTypeID')  # Field name made lowercase.
    manufacturerid = models.ForeignKey('Manufacturers', models.DO_NOTHING, db_column='ManufacturerID', blank=True, null=True)  # Field name made lowercase.
    manufacturer = models.CharField(db_column='Manufacturer', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    model = models.CharField(db_column='Model', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    functionaldescription = models.CharField(db_column='FunctionalDescription', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    processvariable = models.CharField(db_column='ProcessVariable', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    servicedescription = models.CharField(db_column='ServiceDescription', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fluidtype = models.CharField(db_column='FluidType', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fluidcomposition = models.CharField(db_column='FluidComposition', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    measurementrangemin = models.DecimalField(db_column='MeasurementRangeMin', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    measurementrangemax = models.DecimalField(db_column='MeasurementRangeMax', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    measurementunit = models.CharField(db_column='MeasurementUnit', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    outputrangemin = models.DecimalField(db_column='OutputRangeMin', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    outputrangemax = models.DecimalField(db_column='OutputRangeMax', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    outputunit = models.CharField(db_column='OutputUnit', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    accuracy = models.CharField(db_column='Accuracy', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    repeatability = models.CharField(db_column='Repeatability', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rangeability = models.CharField(db_column='Rangeability', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    responsetime = models.CharField(db_column='ResponseTime', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    locationdescription = models.CharField(db_column='LocationDescription', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    installationdrawing = models.CharField(db_column='InstallationDrawing', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pidnumber = models.CharField(db_column='PIDNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pipelineid = models.CharField(db_column='PipelineID', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    elevationlevel = models.CharField(db_column='ElevationLevel', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gridreference = models.CharField(db_column='GridReference', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mountingtype = models.CharField(db_column='MountingType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    processconnection = models.CharField(db_column='ProcessConnection', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    materialofconstruction = models.CharField(db_column='MaterialOfConstruction', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    wetpartsmaterial = models.CharField(db_column='WetPartsMaterial', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gasketmaterial = models.CharField(db_column='GasketMaterial', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    powersupply = models.CharField(db_column='PowerSupply', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    powerconsumption = models.CharField(db_column='PowerConsumption', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    signaltype = models.CharField(db_column='SignalType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    communicationprotocol = models.CharField(db_column='CommunicationProtocol', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    wiringdiagram = models.CharField(db_column='WiringDiagram', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    junctionboxnumber = models.CharField(db_column='JunctionBoxNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cabletag = models.CharField(db_column='CableTag', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cabletype = models.CharField(db_column='CableType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cablelength_meters = models.DecimalField(db_column='CableLength_Meters', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iocardlocation = models.CharField(db_column='IOCardLocation', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    iocardtype = models.CharField(db_column='IOCardType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dcsaddress = models.CharField(db_column='DCSAddress', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    modbusaddress = models.IntegerField(db_column='ModbusAddress', blank=True, null=True)  # Field name made lowercase.
    issafetyinstrument = models.BooleanField(db_column='IsSafetyInstrument', blank=True, null=True)  # Field name made lowercase.
    sil_rating = models.CharField(db_column='SIL_Rating', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sif_number = models.CharField(db_column='SIF_Number', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    atex_rating = models.CharField(db_column='ATEX_Rating', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    atex_certificate = models.CharField(db_column='ATEX_Certificate', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ip_rating = models.CharField(db_column='IP_Rating', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nema_rating = models.CharField(db_column='NEMA_Rating', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    iecex_rating = models.CharField(db_column='IECEx_Rating', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hasalarm = models.BooleanField(db_column='HasAlarm', blank=True, null=True)  # Field name made lowercase.
    alarmcount = models.IntegerField(db_column='AlarmCount', blank=True, null=True)  # Field name made lowercase.
    hastrip = models.BooleanField(db_column='HasTrip', blank=True, null=True)  # Field name made lowercase.
    tripcount = models.IntegerField(db_column='TripCount', blank=True, null=True)  # Field name made lowercase.
    isinterlock = models.BooleanField(db_column='IsInterlock', blank=True, null=True)  # Field name made lowercase.
    isredundant = models.BooleanField(db_column='IsRedundant', blank=True, null=True)  # Field name made lowercase.
    redundantpair = models.ForeignKey('self', models.DO_NOTHING, db_column='RedundantPair', blank=True, null=True)  # Field name made lowercase.
    redundancytype = models.CharField(db_column='RedundancyType', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isoperational = models.BooleanField(db_column='IsOperational', blank=True, null=True)  # Field name made lowercase.
    isbypassed = models.BooleanField(db_column='IsByPassed', blank=True, null=True)  # Field name made lowercase.
    bypassreason = models.CharField(db_column='ByPassReason', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    bypassdate = models.DateTimeField(db_column='ByPassDate', blank=True, null=True)  # Field name made lowercase.
    bypassapprovedby = models.CharField(db_column='ByPassApprovedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    criticality = models.CharField(db_column='Criticality', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fmea_rpn = models.IntegerField(db_column='FMEA_RPN', blank=True, null=True)  # Field name made lowercase.
    maintenancepriority = models.CharField(db_column='MaintenancePriority', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    purchasedate = models.DateField(db_column='PurchaseDate', blank=True, null=True)  # Field name made lowercase.
    purchaseordernumber = models.CharField(db_column='PurchaseOrderNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    purchasecost = models.DecimalField(db_column='PurchaseCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    costcurrency = models.CharField(db_column='CostCurrency', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    deliverydate = models.DateField(db_column='DeliveryDate', blank=True, null=True)  # Field name made lowercase.
    installationdate = models.DateField(db_column='InstallationDate', blank=True, null=True)  # Field name made lowercase.
    commissiondate = models.DateField(db_column='CommissionDate', blank=True, null=True)  # Field name made lowercase.
    startupdate = models.DateField(db_column='StartupDate', blank=True, null=True)  # Field name made lowercase.
    warrantyperiod_months = models.IntegerField(db_column='WarrantyPeriod_Months', blank=True, null=True)  # Field name made lowercase.
    warrantystartdate = models.DateField(db_column='WarrantyStartDate', blank=True, null=True)  # Field name made lowercase.
    warrantyexpirydate = models.DateField(db_column='WarrantyExpiryDate', blank=True, null=True)  # Field name made lowercase.
    isunderwarranty = models.IntegerField(db_column='IsUnderWarranty')  # Field name made lowercase.
    calibrationrequired = models.BooleanField(db_column='CalibrationRequired', blank=True, null=True)  # Field name made lowercase.
    calibrationinterval_days = models.IntegerField(db_column='CalibrationInterval_Days', blank=True, null=True)  # Field name made lowercase.
    lastcalibrationdate = models.DateField(db_column='LastCalibrationDate', blank=True, null=True)  # Field name made lowercase.
    calibrationduedate = models.DateField(db_column='CalibrationDueDate', blank=True, null=True)  # Field name made lowercase.
    calibrationstatus = models.CharField(db_column='CalibrationStatus', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    nextcalibrationdate = models.DateField(db_column='NextCalibrationDate', blank=True, null=True)  # Field name made lowercase.
    totalcalibrationsperformed = models.IntegerField(db_column='TotalCalibrationsPerformed', blank=True, null=True)  # Field name made lowercase.
    maintenanceinterval_days = models.IntegerField(db_column='MaintenanceInterval_Days', blank=True, null=True)  # Field name made lowercase.
    lastmaintenancedate = models.DateField(db_column='LastMaintenanceDate', blank=True, null=True)  # Field name made lowercase.
    nextmaintenancedate = models.DateField(db_column='NextMaintenanceDate', blank=True, null=True)  # Field name made lowercase.
    totalmaintenanceperformed = models.IntegerField(db_column='TotalMaintenancePerformed', blank=True, null=True)  # Field name made lowercase.
    installationrunninghours = models.IntegerField(db_column='InstallationRunningHours', blank=True, null=True)  # Field name made lowercase.
    totalfailures = models.IntegerField(db_column='TotalFailures', blank=True, null=True)  # Field name made lowercase.
    mtbf_hours = models.DecimalField(db_column='MTBF_Hours', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mttr_hours = models.DecimalField(db_column='MTTR_Hours', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    availability_percent = models.DecimalField(db_column='Availability_Percent', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    datasheetpath = models.CharField(db_column='DatasheetPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    manualpath = models.CharField(db_column='ManualPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    drawingpath = models.CharField(db_column='DrawingPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    certificatepath = models.CharField(db_column='CertificatePath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    loopnumber = models.CharField(db_column='LoopNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    loopdiagram = models.CharField(db_column='LoopDiagram', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ispartofcontrolloop = models.BooleanField(db_column='IsPartOfControlLoop', blank=True, null=True)  # Field name made lowercase.
    controllertag = models.CharField(db_column='ControllerTag', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    finalcontrolelement = models.CharField(db_column='FinalControlElement', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    specialrequirements = models.CharField(db_column='SpecialRequirements', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    operatinginstructions = models.CharField(db_column='OperatingInstructions', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    safetynotes = models.CharField(db_column='SafetyNotes', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    modifiedby = models.CharField(db_column='ModifiedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    modifieddate = models.DateTimeField(db_column='ModifiedDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Instruments'


class Maintenancerecords(models.Model):
    maintenanceid = models.AutoField(db_column='MaintenanceID', primary_key=True)  # Field name made lowercase.
    instrumentid = models.ForeignKey(Instruments, models.DO_NOTHING, db_column='InstrumentID')  # Field name made lowercase.
    workordernumber = models.CharField(db_column='WorkOrderNumber', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    workordertype = models.CharField(db_column='WorkOrderType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    scheduleddate = models.DateField(db_column='ScheduledDate', blank=True, null=True)  # Field name made lowercase.
    requesteddate = models.DateField(db_column='RequestedDate', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    completiondate = models.DateTimeField(db_column='CompletionDate', blank=True, null=True)  # Field name made lowercase.
    maintenancetype = models.CharField(db_column='MaintenanceType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maintenancecategory = models.CharField(db_column='MaintenanceCategory', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    priority = models.CharField(db_column='Priority', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    requestedby = models.CharField(db_column='RequestedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    assignedto = models.CharField(db_column='AssignedTo', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    technicianid = models.IntegerField(db_column='TechnicianID', blank=True, null=True)  # Field name made lowercase.
    supervisorid = models.IntegerField(db_column='SupervisorID', blank=True, null=True)  # Field name made lowercase.
    contractorname = models.CharField(db_column='ContractorName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    problemdescription = models.CharField(db_column='ProblemDescription', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    symptomobserved = models.CharField(db_column='SymptomObserved', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rootcause = models.CharField(db_column='RootCause', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rootcausecategory = models.CharField(db_column='RootCauseCategory', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    failuremode = models.CharField(db_column='FailureMode', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    workperformed = models.CharField(db_column='WorkPerformed', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    actiontaken = models.CharField(db_column='ActionTaken', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    partsreplaced = models.CharField(db_column='PartsReplaced', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    testingperformed = models.CharField(db_column='TestingPerformed', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    testresults = models.CharField(db_column='TestResults', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    calibrationperformed = models.BooleanField(db_column='CalibrationPerformed', blank=True, null=True)  # Field name made lowercase.
    functionaltestpassed = models.BooleanField(db_column='FunctionalTestPassed', blank=True, null=True)  # Field name made lowercase.
    downtimestart = models.DateTimeField(db_column='DowntimeStart', blank=True, null=True)  # Field name made lowercase.
    downtimeend = models.DateTimeField(db_column='DowntimeEnd', blank=True, null=True)  # Field name made lowercase.
    downtimeduration_hours = models.IntegerField(db_column='DowntimeDuration_Hours', blank=True, null=True)  # Field name made lowercase.
    planneddowntime = models.BooleanField(db_column='PlannedDowntime', blank=True, null=True)  # Field name made lowercase.
    productionimpact = models.CharField(db_column='ProductionImpact', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    laborhours = models.DecimalField(db_column='LaborHours', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    laborcost = models.DecimalField(db_column='LaborCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    partscost = models.DecimalField(db_column='PartsCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    contractorcost = models.DecimalField(db_column='ContractorCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    othercosts = models.DecimalField(db_column='OtherCosts', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalcost = models.DecimalField(db_column='TotalCost', max_digits=21, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iswarrantyclaim = models.BooleanField(db_column='IsWarrantyClaim', blank=True, null=True)  # Field name made lowercase.
    warrantyclaimnumber = models.CharField(db_column='WarrantyClaimNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    warrantyapproved = models.BooleanField(db_column='WarrantyApproved', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    requiresfollowup = models.BooleanField(db_column='RequiresFollowUp', blank=True, null=True)  # Field name made lowercase.
    followupdate = models.DateField(db_column='FollowUpDate', blank=True, null=True)  # Field name made lowercase.
    followupaction = models.CharField(db_column='FollowUpAction', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    recommendations = models.CharField(db_column='Recommendations', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    preventiveactions = models.CharField(db_column='PreventiveActions', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    permitrequired = models.BooleanField(db_column='PermitRequired', blank=True, null=True)  # Field name made lowercase.
    permitnumber = models.CharField(db_column='PermitNumber', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hotworkpermit = models.BooleanField(db_column='HotWorkPermit', blank=True, null=True)  # Field name made lowercase.
    confinedspacepermit = models.BooleanField(db_column='ConfinedSpacePermit', blank=True, null=True)  # Field name made lowercase.
    attachmentpath = models.CharField(db_column='AttachmentPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MaintenanceRecords'


class Manufacturers(models.Model):
    manufacturerid = models.AutoField(db_column='ManufacturerID', primary_key=True)  # Field name made lowercase.
    manufacturername = models.CharField(db_column='ManufacturerName', unique=True, max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    shortname = models.CharField(db_column='ShortName', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contactemail = models.CharField(db_column='ContactEmail', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contactphone = models.CharField(db_column='ContactPhone', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    localrepresentative = models.CharField(db_column='LocalRepresentative', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    localrepphone = models.CharField(db_column='LocalRepPhone', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    localrepemail = models.CharField(db_column='LocalRepEmail', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isapprovedvendor = models.BooleanField(db_column='IsApprovedVendor', blank=True, null=True)  # Field name made lowercase.
    qualityrating = models.DecimalField(db_column='QualityRating', max_digits=3, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    deliveryrating = models.DecimalField(db_column='DeliveryRating', max_digits=3, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    technicalsupportrating = models.DecimalField(db_column='TechnicalSupportRating', max_digits=3, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    hasservicecenter = models.BooleanField(db_column='HasServiceCenter', blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Manufacturers'


class Processunits(models.Model):
    unitid = models.AutoField(db_column='UnitID', primary_key=True)  # Field name made lowercase.
    siteid = models.ForeignKey('Sites', models.DO_NOTHING, db_column='SiteID')  # Field name made lowercase.
    unitcode = models.CharField(db_column='UnitCode', unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    unitname = models.CharField(db_column='UnitName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    unittype = models.CharField(db_column='UnitType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    designcapacity = models.DecimalField(db_column='DesignCapacity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    capacityunit = models.CharField(db_column='CapacityUnit', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    operatingpressure = models.DecimalField(db_column='OperatingPressure', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    operatingtemperature = models.DecimalField(db_column='OperatingTemperature', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pressureunit = models.CharField(db_column='PressureUnit', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    temperatureunit = models.CharField(db_column='TemperatureUnit', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    commissiondate = models.DateField(db_column='CommissionDate', blank=True, null=True)  # Field name made lowercase.
    operationalstatus = models.CharField(db_column='OperationalStatus', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hazardclass = models.CharField(db_column='HazardClass', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    atex_zone = models.CharField(db_column='ATEX_Zone', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sil_level = models.CharField(db_column='SIL_Level', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isoperational = models.BooleanField(db_column='IsOperational', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProcessUnits'


class Sites(models.Model):
    siteid = models.AutoField(db_column='SiteID', primary_key=True)  # Field name made lowercase.
    sitecode = models.CharField(db_column='SiteCode', unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    sitename = models.CharField(db_column='SiteName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    sitetype = models.CharField(db_column='SiteType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    gps_latitude = models.DecimalField(db_column='GPS_Latitude', max_digits=10, decimal_places=8, blank=True, null=True)  # Field name made lowercase.
    gps_longitude = models.DecimalField(db_column='GPS_Longitude', max_digits=11, decimal_places=8, blank=True, null=True)  # Field name made lowercase.
    capacity = models.CharField(db_column='Capacity', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    commissiondate = models.DateField(db_column='CommissionDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sites'


class Spareparts(models.Model):
    sparepartid = models.AutoField(db_column='SparePartID', primary_key=True)  # Field name made lowercase.
    partnumber = models.CharField(db_column='PartNumber', unique=True, max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    manufacturerpartnumber = models.CharField(db_column='ManufacturerPartNumber', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alternatepartnumber = models.CharField(db_column='AlternatePartNumber', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    partname = models.CharField(db_column='PartName', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    partcategory = models.CharField(db_column='PartCategory', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    partsubcategory = models.CharField(db_column='PartSubCategory', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parttype = models.CharField(db_column='PartType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    manufacturerid = models.ForeignKey(Manufacturers, models.DO_NOTHING, db_column='ManufacturerID', blank=True, null=True)  # Field name made lowercase.
    manufacturername = models.CharField(db_column='ManufacturerName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    instrumenttypeid = models.ForeignKey(Instrumenttypes, models.DO_NOTHING, db_column='InstrumentTypeID', blank=True, null=True)  # Field name made lowercase.
    compatiblemodels = models.CharField(db_column='CompatibleModels', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    compatibletags = models.CharField(db_column='CompatibleTags', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    interchangeable = models.BooleanField(db_column='Interchangeable', blank=True, null=True)  # Field name made lowercase.
    interchangeablewith = models.CharField(db_column='InterchangeableWith', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    technicalspecs = models.CharField(db_column='TechnicalSpecs', max_length=2000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    material = models.CharField(db_column='Material', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dimensions = models.CharField(db_column='Dimensions', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    weight_kg = models.DecimalField(db_column='Weight_Kg', max_digits=10, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    unitofmeasure = models.CharField(db_column='UnitOfMeasure', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    unitcost = models.DecimalField(db_column='UnitCost', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    currency = models.CharField(db_column='Currency', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lastpurchaseprice = models.DecimalField(db_column='LastPurchasePrice', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lastpurchasedate = models.DateField(db_column='LastPurchaseDate', blank=True, null=True)  # Field name made lowercase.
    pricevaliduntil = models.DateField(db_column='PriceValidUntil', blank=True, null=True)  # Field name made lowercase.
    primarysupplier = models.CharField(db_column='PrimarySupplier', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    primarysuppliercontact = models.CharField(db_column='PrimarySupplierContact', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alternativesupplier1 = models.CharField(db_column='AlternativeSupplier1', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    alternativesupplier2 = models.CharField(db_column='AlternativeSupplier2', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    leadtime_days = models.IntegerField(db_column='LeadTime_Days', blank=True, null=True)  # Field name made lowercase.
    leadtimecategory = models.CharField(db_column='LeadTimeCategory', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emergencyprocurement = models.BooleanField(db_column='EmergencyProcurement', blank=True, null=True)  # Field name made lowercase.
    emergencysupplier = models.CharField(db_column='EmergencySupplier', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    minstocklevel = models.IntegerField(db_column='MinStockLevel', blank=True, null=True)  # Field name made lowercase.
    maxstocklevel = models.IntegerField(db_column='MaxStockLevel', blank=True, null=True)  # Field name made lowercase.
    reorderpoint = models.IntegerField(db_column='ReorderPoint', blank=True, null=True)  # Field name made lowercase.
    reorderquantity = models.IntegerField(db_column='ReorderQuantity', blank=True, null=True)  # Field name made lowercase.
    safetystock = models.IntegerField(db_column='SafetyStock', blank=True, null=True)  # Field name made lowercase.
    economicorderquantity = models.IntegerField(db_column='EconomicOrderQuantity', blank=True, null=True)  # Field name made lowercase.
    annualusage = models.IntegerField(db_column='AnnualUsage', blank=True, null=True)  # Field name made lowercase.
    averagemonthlyusage = models.DecimalField(db_column='AverageMonthlyUsage', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lastuseddate = models.DateField(db_column='LastUsedDate', blank=True, null=True)  # Field name made lowercase.
    usagefrequency = models.CharField(db_column='UsageFrequency', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    criticality = models.CharField(db_column='Criticality', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isinsurancespare = models.BooleanField(db_column='IsInsuranceSpare', blank=True, null=True)  # Field name made lowercase.
    iscriticalspare = models.BooleanField(db_column='IsCriticalSpare', blank=True, null=True)  # Field name made lowercase.
    islongleaditem = models.BooleanField(db_column='IsLongLeadItem', blank=True, null=True)  # Field name made lowercase.
    hasshelflife = models.BooleanField(db_column='HasShelfLife', blank=True, null=True)  # Field name made lowercase.
    shelflife_months = models.IntegerField(db_column='ShelfLife_Months', blank=True, null=True)  # Field name made lowercase.
    requiresspecialstorage = models.BooleanField(db_column='RequiresSpecialStorage', blank=True, null=True)  # Field name made lowercase.
    storageconditions = models.CharField(db_column='StorageConditions', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    requirescertification = models.BooleanField(db_column='RequiresCertification', blank=True, null=True)  # Field name made lowercase.
    certificationtype = models.CharField(db_column='CertificationType', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    qualitystandard = models.CharField(db_column='QualityStandard', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isobsolete = models.BooleanField(db_column='IsObsolete', blank=True, null=True)  # Field name made lowercase.
    obsolescencedate = models.DateField(db_column='ObsolescenceDate', blank=True, null=True)  # Field name made lowercase.
    obsolescencereason = models.CharField(db_column='ObsolescenceReason', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    replacementpartnumber = models.CharField(db_column='ReplacementPartNumber', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    warrantyperiod_months = models.IntegerField(db_column='WarrantyPeriod_Months', blank=True, null=True)  # Field name made lowercase.
    warrantyterms = models.CharField(db_column='WarrantyTerms', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    datasheetpath = models.CharField(db_column='DatasheetPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    drawingpath = models.CharField(db_column='DrawingPath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    imagepath = models.CharField(db_column='ImagePath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    certificatepath = models.CharField(db_column='CertificatePath', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ishazardousmaterial = models.BooleanField(db_column='IsHazardousMaterial', blank=True, null=True)  # Field name made lowercase.
    msds_path = models.CharField(db_column='MSDS_Path', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    handlinginstructions = models.CharField(db_column='HandlingInstructions', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    disposalrequirements = models.CharField(db_column='DisposalRequirements', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    modifiedby = models.CharField(db_column='ModifiedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    modifieddate = models.DateTimeField(db_column='ModifiedDate', blank=True, null=True)  # Field name made lowercase.
    lastreviewdate = models.DateField(db_column='LastReviewDate', blank=True, null=True)  # Field name made lowercase.
    nextreviewdate = models.DateField(db_column='NextReviewDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='IsApproved', blank=True, null=True)  # Field name made lowercase.
    approvedby = models.CharField(db_column='ApprovedBy', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    approvaldate = models.DateField(db_column='ApprovalDate', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SpareParts'


class Subsystems(models.Model):
    subsystemid = models.AutoField(db_column='SubSystemID', primary_key=True)  # Field name made lowercase.
    unitid = models.ForeignKey(Processunits, models.DO_NOTHING, db_column='UnitID')  # Field name made lowercase.
    subsystemcode = models.CharField(db_column='SubSystemCode', unique=True, max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    subsystemname = models.CharField(db_column='SubSystemName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SubSystems'


class Tripinstruments(models.Model):
    tripinstrumentid = models.AutoField(db_column='TripInstrumentID', primary_key=True)  # Field name made lowercase.
    tripid = models.ForeignKey('Tripsinterlocks', models.DO_NOTHING, db_column='TripID')  # Field name made lowercase.
    instrumentid = models.ForeignKey(Instruments, models.DO_NOTHING, db_column='InstrumentID')  # Field name made lowercase.
    votinglogic = models.CharField(db_column='VotingLogic', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isprimary = models.BooleanField(db_column='IsPrimary', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TripInstruments'


class Tripsinterlocks(models.Model):
    tripid = models.AutoField(db_column='TripID', primary_key=True)  # Field name made lowercase.
    triptag = models.CharField(db_column='TripTag', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    tripdescription = models.CharField(db_column='TripDescription', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    triptype = models.CharField(db_column='TripType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    triplogic = models.CharField(db_column='TripLogic', max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sil_level = models.CharField(db_column='SIL_Level', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    initiatinginstruments = models.CharField(db_column='InitiatingInstruments', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    affectedequipment = models.CharField(db_column='AffectedEquipment', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    tripsetpoint = models.DecimalField(db_column='TripSetpoint', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tripresetcondition = models.CharField(db_column='TripResetCondition', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isautoreset = models.BooleanField(db_column='IsAutoReset', blank=True, null=True)  # Field name made lowercase.
    requirespermittoreset = models.BooleanField(db_column='RequiresPermitToReset', blank=True, null=True)  # Field name made lowercase.
    testfrequency_days = models.IntegerField(db_column='TestFrequency_Days', blank=True, null=True)  # Field name made lowercase.
    lasttestdate = models.DateField(db_column='LastTestDate', blank=True, null=True)  # Field name made lowercase.
    nexttestdate = models.DateField(db_column='NextTestDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TripsInterlocks'
