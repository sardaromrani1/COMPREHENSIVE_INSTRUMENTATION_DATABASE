# Comprehensive Instrumentation Database
A Microsoft SQL Server–based Instrumentation Asset Management, Maintenance Management, and Reliability Analytics System with a Python Tkinter Desktop Application.
## Overview
The Comprehensive Instrumentation Database is an industrial database project designed for instrumentation engineers, maintenance engineers, database developers, and reliability professionals.
The project demonstrates how Microsoft SQL Server can be used to build a normalized industrial database that supports:
Instrument asset management
Preventive and corrective maintenance
Failure history management
Reliability engineering
Maintenance cost analysis
Spare parts management
Industrial analytics
Desktop application development using Python
The repository combines SQL Server database design with a modular Python desktop application that provides a graphical interface for managing instrumentation data.

# Features
## Database
Fully normalized SQL Server database
Relational data model
Foreign key constraints
Reference tables
Transaction tables
Analytical SQL Views
Window Functions
KPI calculations
Dashboard queries
## Instrumentation
Instrument master data
Instrument types
Manufacturers
Process units
Control systems
Spare parts
Calibration records
Maintenance records
Failure records
## Analytics
The project includes SQL queries for:
MTTR
MTBF
Failure Frequency
Downtime Analysis
Maintenance Cost
Labor Hours
Spare Part Consumption
Reliability KPIs

# Technology Stack
## Technology
## Description
Microsoft SQL Server
Relational Database
T-SQL
Database Programming
Python
Desktop Application
Tkinter
GUI Framework
pyodbc
SQL Server Connectivity
Git
Version Control
GitHub
Repository Hosting

# Repository Structure
COMPREHENSIVE_INSTRUMENTATION_DATABASE
│
├── ANALYTICS/
│
├── Data_Modeling_and_Analytics/
│
├── INSERT/
│
├── QUERY/
│
├── VIEW/
│
├── WINDOW_Functions/
│
├── sql-schema/
│
├── MAINTENANCE&RELIABILITY_DASHBOARD/
│
├── Python_Project/
│ │
│ ├── db_connection.py
│ ├── main.py
│ ├── Instruments_form.py
│ ├── FailureRecords_form.py
│ ├── MaintenanceRecords_form.py
│ ├── ...
│
├── SQLQuery_CREATE_DATABASE.sql
│
└── README.md

# Python Desktop Application
The Python_Project directory contains a modular desktop application developed using Tkinter.
## Main Components

db_connection.py

Provides SQL Server connectivity using pyodbc.

Responsible for:

Opening database connections

Connection reuse

SQL Server authentication


## main.py

Application entry point.

Responsible for:

Creating the main window

Navigation

Launching forms


## GUI Forms

Each table has an independent CRUD interface.

Examples:

Instruments

Failure Records

Maintenance Records

Calibration Records

Manufacturers

Spare Parts


Each form supports:

Insert

Update

Delete

Search

Clear Form


# Database Architecture
                SQL Server
                     │
      ┌──────────────┴──────────────┐
      │ │
 Master Tables Transaction Tables
      │ │
      └──────────────┬──────────────┘
                     │
              Analytical Views
                     │
             Dashboard Queries
                     │
      Python Tkinter Desktop GUI

# Database Layers

## Reference Data

Contains relatively static information.

Examples

Instruments

Manufacturers

Instrument Types

Units

Control Systems


## Transaction Data

Stores operational history.

Examples

Maintenance Records

Failure Records

Calibration Records

Spare Part Consumption


## Analytics Layer

Provides reusable SQL Views for reporting.

Examples

MTTR

Downtime

Maintenance Costs

Labor Utilization

Failure Statistics


# Installation

## Requirements

Microsoft SQL Server

SQL Server Management Studio

Python 3.11+

ODBC Driver 17 or 18 for SQL Server


## Python Packages

Install dependencies

pip install pyodbc


# Database Setup

Create the database.

CREATE DATABASE ComprehensiveInstrumentationDB;

Execute SQL scripts in the following order.

Database creation

Tables

Constraints

Reference data

Sample data

Views

Analytical queries


# Running the Application
Configure the SQL Server connection inside

Python_Project/db_connection.py

Update:

SERVER = "YOUR_SERVER\\SQLEXPRESS"

DATABASE = "ComprehensiveInstrumentationDB"

Run

python main.py


# Example Analytical Queries

The repository demonstrates advanced SQL including

JOINs

Common Table Expressions (CTEs)

Window Functions

Aggregate Functions

Ranking Functions

Date Functions

CASE Expressions

Views

KPI Calculations


# Intended Use Cases

This repository can be used for

Instrumentation Management

Maintenance Engineering

Reliability Engineering

SQL Server Learning

Database Design

Python Database Applications

Data Analytics

Portfolio Demonstration


# Future Enhancements

Planned improvements include

Django Web Application

REST API

Power BI Dashboard

Predictive Maintenance

Machine Learning Models

Inventory Optimization

User Authentication

Role-Based Access Control

SQL Server Index Optimization


# Author

Sardar Omrani

Database Engineer | Instrumentation Maintenance Engineer

Specializations

Microsoft SQL Server

Database Design

Python Development

Industrial Data Analytics

Instrumentation Systems

Maintenance & Reliability Engineering


# License

This repository is provided for educational, research, and portfolio purposes
