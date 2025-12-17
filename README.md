# Comprehensive Instrumentation & Maintenance Database

SQL Server–Based Industrial Analytics Solution

## 1. Project Definition (Business Perspective)
### Problem Statement

Industrial plants (refineries, power plants, process industries) generate large volumes of instrumentation and maintenance data, but this data is often:

Fragmented across systems

Poorly structured for analysis

Difficult to use for reliability KPIs and decision-making

As a result, maintenance teams struggle to:

Measure equipment reliability

Analyze downtime and failure patterns

Control maintenance costs

Forecast spare-part demand

### Solution Overview

This project implements a SQL Server–based relational database designed specifically to support:

Instrumentation asset management

Maintenance history tracking

Downtime and failure analysis

Reliability and cost KPIs

Analytics-ready views for BI and reporting tools

The database is designed to act as a single source of truth for maintenance and reliability analytics in an industrial environment.

### Business Value

The solution enables organizations to:

Monitor MTTR (Mean Time To Repair)

Quantify downtime impact

Analyze maintenance cost and labor

Support data-driven maintenance planning

Provide clean, structured data for dashboards and analytics

## 2. Technology Stack

Database Platform: Microsoft SQL Server

Language: T-SQL

Techniques Used:

Relational data modeling

Views and layered analytical views

CTEs (Common Table Expressions)

Time-based aggregations

KPI calculations

Target Consumers:

Power BI / SSRS

Python analytics (pandas, pyodbc)

Web backends (e.g., Django)

## 3. Data Model Overview

The database follows a clean separation of concerns:

3.1 Master (Reference) Data

Defines what exists in the plant:

Instruments

Manufacturers

Models

Locations / units

Spare parts

These tables are stable and change infrequently.

3.2 Transactional Data

Captures what happens over time:

Maintenance records

Failures

Downtime events

Spare-part consumption

Labor hours

These tables form the historical backbone of the system.

3.3 Analytical Views

Transform raw data into decision-ready KPIs:

MTTR per instrument

Total downtime summaries

Maintenance cost aggregation

Labor utilization metrics

Combined maintenance dashboard view

Views are intentionally used to:

Centralize business logic

Simplify BI tool integration

Ensure consistent KPI definitions

## 4. Key KPIs Implemented

The project includes SQL views that calculate:

MTTR (Mean Time To Repair)

Total Downtime (hours)

Maintenance Cost per Instrument

Average Labor Hours

Short-term spare-part demand forecast (moving average)

These KPIs reflect real industrial maintenance practices, not synthetic examples.

## 5. Repository Structure (Recommended)

/schema
   01_tables.sql
   02_constraints.sql

/data
   sample_instruments.sql
   sample_maintenance.sql

/views
   v_MTTR.sql
   v_DowntimeSummary.sql
   v_MaintenanceDashboard.sql

/security
   create_roles.sql

/docs
   ER_diagram.png

This structure supports:

Easy setup

Clear separation of concerns

Professional maintainability

## 6. How to Run the Project Locally

1. Create an empty database in SQL Server
CREATE DATABASE InstrumentationDB;

2. Execute scripts in this order:

Schema (tables & constraints)

Sample data (optional)

3. Validate objects:
SELECT * FROM sys.tables;
SELECT * FROM sys.views;

4. Query the dashboard view:
SELECT * FROM v_MaintenanceDashboard;

## 7. Security Model (Example)

The project demonstrates role-based access control:

Analyst role: read-only access for reporting

Writer role: controlled insert/update for maintenance data

This reflects real enterprise security practices.

##8. Design Decisions

Views instead of stored procedures
→ Better compatibility with BI tools and analytics workflows

Normalized core + analytical layer
→ Data integrity with analytics flexibility

SQL Server
→ Widely used in industrial and enterprise environments

##9. Intended Use Cases

Maintenance & reliability analytics

Industrial data analysis portfolios

SQL Developer / Data Analyst demonstrations

Backend data source for dashboards and applications

## 8. Design Decisions

Views instead of stored procedures
→ Better compatibility with BI tools and analytics workflows

Normalized core + analytical layer
→ Data integrity with analytics flexibility

SQL Server
→ Widely used in industrial and enterprise environments

## 9. Intended Use Cases

Maintenance & reliability analytics

Industrial data analysis portfolios

SQL Developer / Data Analyst demonstrations

Backend data source for dashboards and applications

## 10. About the Author

This project is based on real industrial maintenance and instrumentation concepts and reflects:

Practical domain knowledge

Production-oriented SQL design

Analytics-focused data modeling

## Status

Actively evolving — additional features such as indexing strategy, BI dashboards, and API integration can be layered on top.
