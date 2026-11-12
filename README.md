# Top-Spec Plumbing & Drainage — Database Management System

A desktop business and database management application developed in Python for my OCR A-Level Computer Science (H446/03) Programming Project. This project scored **64/70 (Grade A\*)** in the June 2026 examination series.

## Overview
Built for a local plumbing and drainage business, this offline-first desktop application replaces fragmented paper records and manual tracking with a relational database. It handles appointment scheduling, quote and guarantee requests, and invoicing through a graphical interface.

## Key Features
* **Role-Based Access Control (RBAC):** Supports three permission tiers — Main Staff, Staff, and Customers — with hashed password storage using SHA-256 and input validation.
* **Customer Portal:** Allows customers to register, book appointments from available slots, submit quote or one-year guarantee requests, and view their own invoices and job history.
* **Staff & Admin Dashboard:** Enables staff to manage jobs, respond directly to customer requests, and receive automated reminders for upcoming appointments.
* **Invoicing & Income Tracking:** Generates itemised quotes and invoices (including dynamic extra costs) and tracks income by day, week, and month.
* **3NF Relational Database:** Uses a 3NF SQLite backend (`Backend.db`) to eliminate data redundancy and ensure data integrity.

## Tech Stack
* **Language:** Python 3.13
* **GUI Framework:** Tkinter
* **Database:** SQLite3

## Database Architecture
![Entity-Relationship Diagram](ERD%20for%20Programming%20Project.jpg)

## Repository Contents
* `Database Management System.py` — Main application source code containing the Tkinter GUI, validation logic, and database queries.
* `Backend.db` — Pre-configured SQLite database populated strictly with fictional test data *(no real customer or business records are stored)*.
* `watersafe-topspec_edited.gif` — UI branding asset required by the application interface.

## How to Run the Program
1. Ensure Python 3.13 or newer is installed on your system.
2. Ensure that the fpdf module is installed on your system. If you are unsure, go into Command Prompt and type ```pip install fpdf``` to install the module.
3. Clone or download this repository, keeping all three files in the same directory.
4. Run the application from your terminal or IDE:
   ```bash
   python "Database Management System.py"
   ```

> **Note for Testing:** You can register a new customer account directly through the interface.
