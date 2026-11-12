from datetime import datetime
from datetime import timedelta
from datetime import time
import sqlite3
import hashlib
from tkinter import *
import tkinter as tk
from tkinter import ttk
import re
from fpdf import FPDF
from tkinter import messagebox
import os


with sqlite3.connect("Backend.db") as db:
    cursor = db.cursor()


def hash_password(password):
    #hashes the password using SHA-256 and returns the hex digest, all passwords should be stored as hashes
    return hashlib.sha256(password.encode()).hexdigest()

global main_screen
global username
global password
global firstname
global lastname
global emailaddress
global phonenumber
global houseaddress
global postcode
global username_enter_verify 
global password_enter_verify
global firstname_verify
global lastname_verify
global emailaddress_verify
global phonenumber_verify
global houseaddress_verify
global postcode_verify 

#creates the Customers table
cursor.execute('''CREATE TABLE IF NOT EXISTS Customers(
    CustomerID INTEGER NOT NULL PRIMARY KEY,
    CustomerUsername VARCHAR(40) NOT NULL UNIQUE,
    CustomerPassword VARCHAR(100) NOT NULL,
    CustomerFirstName VARCHAR(50) NOT NULL,
    CustomerSurname VARCHAR(50) NOT NULL,
    CustomerEmailAddress VARCHAR(100) NOT NULL,
    CustomerPhoneNumber VARCHAR(15) NOT NULL,
    CustomerHouseAddress VARCHAR(100) NOT NULL,
    CustomerPostcode VARCHAR(20) NOT NULL
);''')

#creates the Jobs table
cursor.execute('''CREATE TABLE IF NOT EXISTS Jobs(
    JobID INTEGER NOT NULL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    JobDescription VARCHAR(100) NOT NULL,
    JobDateAndTime DATETIME NOT NULL UNIQUE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);''')

#creates the RequestQuotes table
cursor.execute('''CREATE TABLE IF NOT EXISTS RequestQuotes(
    RequestQuoteID INTEGER NOT NULL PRIMARY KEY,
    JobID INTEGER,
    CustomerID INTEGER NOT NULL,
    QuoteMessage VARCHAR(100) NOT NULL,
    FOREIGN KEY (JobID) REFERENCES Jobs(JobID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);''')

#creates the Quotes table
cursor.execute('''CREATE TABLE IF NOT EXISTS Quotes(
    QuoteID INTEGER NOT NULL PRIMARY KEY,
    RequestQuoteID INTEGER,
    JobID INTEGER,
    CustomerID INTEGER NOT NULL,
    QuoteEstimatedPrice DECIMAL(10, 2) NOT NULL,
    QuoteDate DATETIME NOT NULL,
    FOREIGN KEY (RequestQuoteID) REFERENCES RequestQuotes(RequestQuoteID),
    FOREIGN KEY (JobID) REFERENCES Jobs(JobID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);''')

#creates the Guarantees table
cursor.execute('''CREATE TABLE IF NOT EXISTS Guarantees(
    GuaranteeID INTEGER NOT NULL PRIMARY KEY,
    JobID INTEGER NOT NULL,
    CustomerID INTEGER NOT NULL,
    GuaranteeMessage VARCHAR(100) NOT NULL,
    GuaranteeApprovedorDenied BOOLEAN,
    GuaranteeDate DATETIME NOT NULL,
    FOREIGN KEY (JobID) REFERENCES Jobs(JobID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);''')

#creates the Invoices table
cursor.execute('''CREATE TABLE IF NOT EXISTS Invoices(
    InvoiceID INTEGER NOT NULL PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    JobID INTEGER NOT NULL,
    QuoteID INTEGER NOT NULL,
    InvoicePrice DECIMAL(10, 2) NOT NULL,
    InvoiceReason VARCHAR(100) NOT NULL,
    InvoiceExtraPrice DECIMAL(10, 2),
    InvoiceDate DATETIME NOT NULL,
    InvoicePaid BOOLEAN,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (JobID) REFERENCES Jobs(JobID),
    FOREIGN KEY (QuoteID) REFERENCES Quotes(QuoteID)
);''')

#creates the Staff table
cursor.execute('''CREATE TABLE IF NOT EXISTS Staff(
    StaffID INTEGER NOT NULL PRIMARY KEY,
    StaffUsername VARCHAR(40) NOT NULL UNIQUE,
    StaffPassword VARCHAR(100) NOT NULL
);''')

#creates the Main Staff table
cursor.execute('''CREATE TABLE IF NOT EXISTS MainStaff(
    MainStaffID INTEGER NOT NULL PRIMARY KEY,
    MainStaffUsername VARCHAR(40) NOT NULL UNIQUE,
    MainStaffPassword VARCHAR(100) NOT NULL
);''')
cursor.execute("PRAGMA foreign_keys = ON;")

def is_valid_sqlite_datetime(datetime_str):
    #Returns True if the string is in YYYY-MM-DD HH:MM:SS format, otherwise False
    SQLITE_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        datetime.strptime(datetime_str, SQLITE_FORMAT)
        return True
    except ValueError:
        return False

def saveappointmentrecord():
    global briefdescriptionjob_entry
    global selecteddatetime_entry
    global CustomerID
    briefdescription_info = briefdescriptionjob_entry.get().strip()
    selecteddatetime_info = selecteddatetime_entry.get().strip()
    if (len(briefdescription_info)==0) or (len(briefdescription_info)>100):
        Label(appointment_screen, text="Error: Brief Description of Job must be between 1 and 100 characters.", fg="red", font=("calibri", 11)).pack()
        briefdescriptionjob_entry.delete(0, END)
    elif (len(selecteddatetime_info)==0) or (not is_valid_sqlite_datetime(selecteddatetime_info)):
        Label(appointment_screen, text="Error: Selected Date and Time must be a valid date and time.", fg="red", font=("calibri", 11)).pack()
        selecteddatetime_entry.delete(0, END)
    elif (CustomerID == ""):
        Label(appointment_screen, text="Error: CustomerID must not be null.", fg="red", font=("calibri",11)).pack()
    else:
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        qrySaveAppointment = "INSERT INTO Jobs (CustomerID, JobDescription, JobDateAndTime) VALUES (?, ?, ?)"
        cursor.execute(qrySaveAppointment, (CustomerID, briefdescription_info, selecteddatetime_info))
        
        conn.commit()
        conn.close()
        Label(appointment_screen, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
        briefdescriptionjob_entry.delete(0, END)
        selecteddatetime_entry.delete(0, END)

def requestnewappointment():
    global CustomerID
    global appointment_screen
    global main_screen
    global customer_main_menu
    global briefdescriptionjob_entry
    global selecteddatetime_entry
    available_options = []
    current_check_date = datetime.now() + timedelta(days=1) # Start checking from tomorrow
    # Define the valid time window
    START_HOUR = 9
    END_HOUR = 17 # 5 PM in 24-hour format
    while len(available_options) < 3:
        for hour in range(START_HOUR, END_HOUR):
            potential_time = datetime.combine(current_check_date.date(), time(hour=hour))
            #Database Booking Check Logic
            time_for_sql = potential_time.strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect("Backend.db")
            cursor = conn.cursor()
            qryGetJobDates = "SELECT JobDateAndTime FROM Jobs WHERE JobDateAndTime = ?"
            cursor.execute(qryGetJobDates, (time_for_sql,)) 
            result = cursor.fetchone()
            is_booked = result is not None 
            #End of Database Booking Check Logic
            #If the slot is *not* booked, add it to the list
            if not is_booked:
                formatted_option = potential_time.strftime("%Y-%m-%d %H:%M:%S")
                available_options.append(formatted_option)
            # Optimization: If we found enough options, break out of the inner loop early
            if len(available_options) >= 3:
                break 
        # This line only runs *after* checking all hours in the inner loop (or breaking early)
        current_check_date += timedelta(days=1)
    customer_main_menu.withdraw()
    appointment_screen = Toplevel(main_screen)
    appointment_screen.geometry("1280x720")
    appointment_screen.title("Request New Appointment (frmNewJobAppointment)")
    Label(appointment_screen, text="Request New Appointment", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(appointment_screen, text="Please enter information into the fields below. "
    "All fields marked with an asterisk (*) are mandatory to fill in.",).pack(pady=10)
    briefdescriptionjob = StringVar()
    selecteddatetime = StringVar()
    #Display CustomerID (label + disabled entry)
    customerID_label = Label(appointment_screen, text="CustomerID *").pack()  # PACK the label!
    customerID_entry = Entry(appointment_screen, width=30, state="disabled", disabledbackground="lightgrey", disabledforeground="black", textvariable=StringVar(value=str(CustomerID))).pack(pady=5)
    #Brief Description of Job
    briefdescriptionjob_label = Label(appointment_screen, text="Brief Description of Job *").pack()
    briefdescriptionjob_entry = Entry(appointment_screen, textvariable=briefdescriptionjob)
    briefdescriptionjob_entry.pack()
    #Selected Date and Time
    selecteddatetime_label = Label(appointment_screen, text="Selected Date and Time *").pack()
    selecteddatetime_entry = ttk.Combobox(
        appointment_screen, 
        textvariable=selecteddatetime, 
        values=available_options, 
        state="readonly"
    )
    selecteddatetime_entry.pack(pady=5)
    #Save Record Button
    Button(appointment_screen, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=saveappointmentrecord).pack()
    if available_options:
        selecteddatetime_entry.set(available_options[0]) 
    def requestnewappointment_on_close():
        customer_main_menu.deiconify()  # Show the main screen again
        appointment_screen.destroy()

    appointment_screen.protocol("WM_DELETE_WINDOW", requestnewappointment_on_close)
    
def GetAppointments(CustomerID):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qrysql = "SELECT JobID, JobDescription, JobDateAndTime FROM Jobs INNER JOIN Customers ON Customers.CustomerID = Jobs.CustomerID WHERE Customers.CustomerID = ?"
    cursor.execute(qrysql, (CustomerID,))
    records = cursor.fetchall()
    conn.close()
    return records
  
    
def ViewAppointments(CustomerID):
    global customer_main_menu
    global viewappointment_screen
    global main_screen
    customer_main_menu.withdraw()
    viewappointment_screen = Toplevel(main_screen)
    viewappointment_screen.geometry("1280x720")
    viewappointment_screen.title("View Appointments (ViewAppointments(CustomerID))")
    Label(viewappointment_screen, text="View Appointments", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(viewappointment_screen, text="All appointments whether prior or current are shown below. Please contact staff if you wish to change appointment details.",).pack(pady=10)
    columns = ("JobID", "JobDescription", "JobDateAndTime")
    tree = ttk.Treeview(viewappointment_screen, columns=columns, show="headings")
    tree.heading("JobID", text="JobID")
    tree.heading("JobDescription", text="Job Description")
    tree.heading("JobDateAndTime", text="Job Date And Time")
    tree.column("JobID", width=50)
    tree.column("JobDescription", width=400)
    tree.column("JobDateAndTime", width=150)
    records = GetAppointments(CustomerID)
    for record in records:
        tree.insert("", tk.END, values=record)
    tree.pack(pady=20, fill=tk.BOTH, expand=True)
    Button(viewappointment_screen, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=viewappointments_on_close).pack()


def viewappointments_on_close():
    global viewappointment_screen
    global customer_main_menu
    customer_main_menu.deiconify()
    viewappointment_screen.destroy()
    
def viewinvoiceguarantees(CustomerID):
    global invoiceguarantee_screen
    global customer_main_menu
    customer_main_menu.withdraw()
    invoiceguarantee_screen = Toplevel(main_screen)
    invoiceguarantee_screen.geometry("1280x720")
    invoiceguarantee_screen.title("View Invoices/Guarantees")
    Label(invoiceguarantee_screen, text="View Invoices/Guarantees", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(invoiceguarantee_screen, text="A PDF document has been generated containing all records.").pack(pady=10)
    invoices = get_customer_invoices_data(CustomerID)
    guarantees = get_customer_guarantees_data(CustomerID)
    quotes = get_customer_quotes_data(CustomerID)
    if invoices or guarantees or quotes:
        pdf_filename = create_customer_records_pdf_combined(CustomerID, invoices, guarantees, quotes)
        messagebox.showinfo("PDF Generated", f"The file {pdf_filename} has been saved and opened.")
        os.startfile(pdf_filename)
    else:
        messagebox.showinfo("No Records", "No records found for this customer.")
    def viewinvoiceguarantee_on_close():
        customer_main_menu.deiconify()  # Show the main screen again
        invoiceguarantee_screen.destroy()

    invoiceguarantee_screen.protocol("WM_DELETE_WINDOW", viewinvoiceguarantee_on_close)

def get_customer_invoices_data(customer_id):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    # Selected 8 columns: 0:InvoiceID, 1:JobID, 2:QuoteID, 3:InvoicePrice, 4:InvoiceReason, 5:InvoiceExtraPrice, 6:InvoiceDate, 7:InvoicePaid
    query = "SELECT InvoiceID, JobID, QuoteID, InvoicePrice, InvoiceReason, InvoiceExtraPrice, InvoiceDate, InvoicePaid FROM Invoices WHERE CustomerID=?"
    cursor.execute(query, (customer_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def get_customer_guarantees_data(customer_id):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    # Selected 5 columns: 0:GuaranteeID, 1:JobID, 2:GuaranteeMessage, 3:GuaranteeApprovedorDenied, 4:GuaranteeDate
    query = "SELECT GuaranteeID, JobID, GuaranteeMessage, GuaranteeApprovedorDenied, GuaranteeDate FROM Guarantees WHERE CustomerID=?"
    cursor.execute(query, (customer_id,))
    records = cursor.fetchall()
    conn.close()
    return records
    
def get_customer_quotes_data(customer_id):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    # Selected 4 columns: 0:QuoteID, 1:JobID, 2:QuoteEstimatedPrice, 3:QuoteDate
    query = "SELECT QuoteID, JobID, QuoteEstimatedPrice, QuoteDate FROM Quotes WHERE CustomerID=?"
    cursor.execute(query, (customer_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def create_customer_records_pdf_combined(CustomerID, invoices, guarantees, quotes):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt="Customer Records Report (ID: %s)" % CustomerID, ln=1, align='C')
    pdf.set_font("Helvetica", '', 12)
    pdf.ln(10)
     # --- INVOICES Section ---
    #0:ID, 1:JobID, 2:QuoteID, 3:Price, 4:Reason, 5:ExtraPrice, 6:Date, 7:Paid
    pdf.set_font('', 'B')
    pdf.cell(0, 10, txt="--- INVOICES ---", ln=1)
    pdf.set_font('', '')
    for inv in invoices:
        #Convert specific indices to float
        price_val = inv[3]
        extra_val = inv[5]
        price = float(price_val) if price_val not in (None, '') else 0.0
        extra = float(extra_val) if extra_val not in (None, '') else 0.0
        paidstatus = "Paid" if str(inv[7]) == '1' else "Outstanding"

        pdf.cell(0, 10, txt="InvoiceID: %s" % inv[0], ln=1)
        pdf.cell(0, 10, txt="JobID: %s" % inv[1], ln=1)
        pdf.cell(0, 10, txt="Invoice Price: £%.2f" % price, ln=1)
        pdf.cell(0, 10, txt="Additional Extra: £%.2f" % extra, ln=1)
        pdf.multi_cell(0, 5, txt="Invoice Reason: %s" % inv[4])
        pdf.cell(0, 10, txt="Invoice Date: %s" % inv[6], ln=1)
        pdf.cell(0, 10, txt="Invoice Paid?: %s" % paidstatus, ln=1) 
        pdf.ln(5)
    # --- GUARANTEES Section ---
    #0:ID, 1:JobID, 2:Message, 3:Status (0/1), 4:Date
    pdf.set_font('', 'B')
    pdf.cell(0, 10, txt="--- GUARANTEES ---", ln=1)
    pdf.set_font('', '')
    for guar in guarantees:
        #Check the status field at index 3
        status = "Approved" if str(guar[3]) == '1' else "Denied"
        
        pdf.cell(0, 10, txt="GuaranteeID: %s" % guar[0], ln=1)
        pdf.cell(0, 10, txt="JobID: %s" % guar[1], ln=1)
        pdf.cell(0, 10, txt="Status: %s" % status, ln=1)
        pdf.multi_cell(0, 5, txt="Guarantee Message: %s" % guar[2])
        pdf.cell(0, 10, txt="Guarantee Date: %s" % guar[4], ln=1)
        pdf.ln(5)
    # --- QUOTES Section ---
    #0:ID, 1:JobID, 2:EstimatedPrice, 3:Date
    pdf.set_font('', 'B')
    pdf.cell(0, 10, txt="--- QUOTES ---", ln=1)
    pdf.set_font('', '')
    for quote in quotes:
        # Convert specific index 2 to float
        est_price = float(quote[2]) if quote[2] is not None else 0.0

        pdf.cell(0, 10, txt="Quote ID: %s" % quote[0], ln=1)
        pdf.cell(0, 10, txt="JobID: %s" % quote[1], ln=1)
        pdf.cell(0, 10, txt="Estimated Price: £%.2f" % est_price, ln=1)
        pdf.cell(0, 10, txt="Quote Date: %s" % quote[3], ln=1)
        pdf.ln(5)
    pdf.set_y(-30)
    pdf.set_font("Helvetica", '', 8)
    pdf.cell(0, 5, txt="Top-Spec Plumbing and Drainage", ln=1)
    pdf.cell(0, 5, txt="http://www.topspecplumbing.co.uk/ | pete@top-specplumbing.com", ln=1)
    pdf.cell(0, 5, txt="07542 499001 | TrustATrader Membership No: TT13835", ln=1)
    pdf.cell(0, 5, txt="Payment Information: Account No: 15518042 | Sort Code: 04-06-05 | Account Holder: Top-Spec Plumbing and Drainage", ln=1)



    filename = "Customer_%s_All_Records.pdf" % CustomerID
    pdf.output(filename, 'F')
    return filename

def savenewquote():
    global CustomerID
    global quote_screen
    global quotemessage_entry
    global jobid_entry
    quotemessage_info = quotemessage_entry.get().strip()
    jobid_info = jobid_entry.get().strip()
    if (len(quotemessage_info)==0) or (len(quotemessage_info)>100):
        Label(quote_screen, text="Error: Quote Message must be between 1 and 100 characters.", fg="red", font=("calibri", 11)).pack()
        quotemessage_entry.delete(0, END)
    elif (CustomerID == ""):
        Label(quote_screen, text="Error: CustomerID must not be null.", fg="red", font=("calibri",11)).pack()
    else:
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        qrySaveRequest = "INSERT INTO RequestQuotes (JobID, CustomerID, QuoteMessage) VALUES (?, ?, ?)"
        cursor.execute(qrySaveRequest, (jobid_info, CustomerID, quotemessage_info))
        
        conn.commit()
        conn.close()
        Label(quote_screen, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
        jobid_entry.delete(0, END)
        quotemessage_entry.delete(0, END)
    
def get_job_ids(CustomerID):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryJobs = "SELECT JobID FROM Jobs INNER JOIN Customers ON Customers.CustomerID = Jobs.CustomerID WHERE Customers.CustomerID = ?"
    cursor.execute(qryJobs, (CustomerID,))
    job_ids = cursor.fetchall()
    flattened_list = [job_id[0] for job_id in job_ids]
    conn.close()
    return flattened_list

def requestnewquote():
    global CustomerID
    global quote_screen
    global main_screen
    global customer_main_menu
    global quotemessage_entry
    global jobid_entry
    customerjobs = get_job_ids(CustomerID)
    customer_main_menu.withdraw()
    quote_screen = Toplevel(main_screen)
    quote_screen.geometry("1280x720")
    quote_screen.title("Request Quote (frmNewQuote)")
    Label(quote_screen, text="Request Quote", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(quote_screen, text="Please enter information into the fields below. "
    "All fields marked with an asterisk (*) are mandatory to fill in.",).pack(pady=10)
    jobid = StringVar()
    quotemessage = StringVar()
    #Display CustomerID (label + disabled entry)
    customerID_label = Label(quote_screen, text="CustomerID *").pack()  # PACK the label!
    customerID_entry = Entry(quote_screen, width=30, state="disabled", disabledbackground="lightgrey", disabledforeground="black", textvariable=StringVar(value=str(CustomerID))).pack(pady=5)
    #Display JobID combobox
    jobid_label = Label(quote_screen, text="JobID ").pack()
    jobid_entry = ttk.Combobox(
        quote_screen, 
        textvariable=jobid, 
        values=customerjobs, 
        state="readonly"
    )
    jobid_entry.pack(pady=5)
    if customerjobs: # Check if the list is not empty before trying to set
        jobid_entry.set(customerjobs[0]) # Sets the first item as the default selection
    #Quote Message
    quotemessage_label = Label(quote_screen, text="Message *").pack()
    quotemessage_entry = Entry(quote_screen, textvariable=quotemessage)
    quotemessage_entry.pack()
    #Save Record Button
    Button(quote_screen, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=savenewquote).pack()
    def requestnewquote_on_close():
        customer_main_menu.deiconify()  # Show the main screen again
        quote_screen.destroy()

    quote_screen.protocol("WM_DELETE_WINDOW", requestnewquote_on_close)
    
   
def savenewguarantee():
    global CustomerID
    global guarantee_screen
    global guaranteemessage_entry
    global jobid_entry
    guaranteemessage_info = guaranteemessage_entry.get().strip()
    jobid_info = jobid_entry.get().strip()
    if (len(guaranteemessage_info)==0) or (len(guaranteemessage_info)>100):
        Label(guarantee_screen, text="Error: Guarantee Message must be between 1 and 100 characters.", fg="red", font=("calibri", 11)).pack()
        guaranteemessage_entry.delete(0, END)
    elif (CustomerID == ""):
        Label(guarantee_screen, text="Error: CustomerID must not be null.", fg="red", font=("calibri",11)).pack()
    elif (jobid_info == ""):
        Label(guarantee_screen, text="Error: JobID must not be null.", fg="red", font=("calibri",11)).pack()
    else:
        current_check_date = datetime.now()
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        qrySaveGuarantee = "INSERT INTO Guarantees (JobID, CustomerID, GuaranteeMessage, GuaranteeDate) VALUES (?, ?, ?, ?)"
        cursor.execute(qrySaveGuarantee, (jobid_info, CustomerID, guaranteemessage_info, current_check_date))
        
        conn.commit()
        conn.close()
        Label(guarantee_screen, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
        jobid_entry.delete(0, END)
        guaranteemessage_entry.delete(0, END)
        
        

def requestnewguarantee():
    global CustomerID
    global guarantee_screen
    global main_screen
    global customer_main_menu
    global guaranteemessage_entry
    global jobid_entry
    jobs = get_job_ids(CustomerID)
    customer_main_menu.withdraw()
    guarantee_screen = Toplevel(main_screen)
    guarantee_screen.geometry("1280x720")
    guarantee_screen.title("Request One-Year Guarantee (frmNewGuarantee)")
    Label(guarantee_screen, text="Request One-Year Guarantee", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(guarantee_screen, text="Please enter information into the fields below. "
    "All fields marked with an asterisk (*) are mandatory to fill in.",).pack(pady=10)
    jobid = StringVar()
    guaranteemessage = StringVar()
    #Display CustomerID (label + disabled entry)
    customerID_label = Label(guarantee_screen, text="CustomerID *").pack()
    customerID_entry = Entry(guarantee_screen, width=30, state="disabled", disabledbackground="lightgrey", disabledforeground="black", textvariable=StringVar(value=str(CustomerID))).pack(pady=5)
    #Display JobID combobox
    jobid_label = Label(guarantee_screen, text="JobID *").pack()
    jobid_entry = ttk.Combobox(
        guarantee_screen, 
        textvariable=jobid, 
        values=jobs, 
        state="readonly"
    )
    jobid_entry.pack(pady=5)
    if jobs: # Check if the list is not empty before trying to set
        jobid_entry.set(jobs[0]) # Sets the first item as the default selection
    #Guarantee Message
    guaranteemessage_label = Label(guarantee_screen, text="Message *").pack()
    guaranteemessage_entry = Entry(guarantee_screen, textvariable=guaranteemessage)
    guaranteemessage_entry.pack()
    #Save Record Button
    Button(guarantee_screen, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=savenewguarantee).pack()
    def requestnewguarantee_on_close():
        customer_main_menu.deiconify()  # Show the main screen again
        guarantee_screen.destroy()

    guarantee_screen.protocol("WM_DELETE_WINDOW", requestnewguarantee_on_close)

def proceed_to_login(logout_screen_instance):
    """Function to be called after the delay."""
    global role
    global CustomerID
    global password_login_entry
    global username_login_entry
    role = ""
    CustomerID = ""
    
    password_login_entry.delete(0, END)
    username_login_entry.delete(0, END)
    main_screen.deiconify()
    logout_screen_instance.destroy()

def logout():
    global staff_main_menu
    global role
    if role == "Staff":
        staff_main_menu.withdraw()
    elif role == "Main Staff":
        main_staff_main_menu.withdraw()
    elif role == "Customer":
        customer_main_menu.withdraw()
    if 'customer_main_menu' in globals() and customer_main_menu.winfo_exists():
        customer_main_menu.withdraw()
    if 'staff_main_menu' in globals() and staff_main_menu.winfo_exists():
        staff_main_menu.withdraw()
    logout_screen = Toplevel(main_screen)
    logout_screen.geometry("1280x720")
    logout_screen.title("Logout User")
    Label(logout_screen, text="Logout User", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(logout_screen, text="Logging out. Please wait...", font=("Calibri", 20)).pack()
    logout_screen.after(2000, proceed_to_login, logout_screen)

    
def customermainmenu():
    global CustomerID
    global customer_main_menu
    global main_screen
    global login_screen
    login_screen.withdraw()
    customer_main_menu = Toplevel(main_screen)
    customer_main_menu.geometry("1280x720")
    customer_main_menu.title("Customer Main Menu")
    Label(customer_main_menu, text="Customer Main Menu", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(customer_main_menu, text="Please click on the relevant option you would like to use in the program.",).pack(pady=10)
    Button(customer_main_menu, text="Request New Appointment", width=30, height=1, command=requestnewappointment).pack()
    Label(customer_main_menu, text="").pack()
    Button(customer_main_menu, text="View Appointments", width=30, height=1, command=lambda: ViewAppointments(CustomerID)).pack()
    Label(customer_main_menu, text="").pack()
    Button(customer_main_menu, text="View Invoices/Guarantees", width=30, height=1, command=lambda: viewinvoiceguarantees(CustomerID)).pack()
    Label(customer_main_menu, text="").pack()
    Button(customer_main_menu, text="Request Quote", width=30, height=1, command=requestnewquote).pack()
    Label(customer_main_menu, text="").pack()
    Button(customer_main_menu, text="Request One Year Guarantee", width=30, height=1, command=requestnewguarantee).pack()
    Label(customer_main_menu, text="").pack()
    Button(customer_main_menu, text="Logout", width=30, height=1, command=logout).pack()
    
def change_record(selectedJobID):
    global update_record
    global briefdescriptionofjob_entry
    global selecteddateandtime_entry
    newJobExplanation = briefdescriptionofjob_entry.get().strip()
    newJobDateAndTime = selecteddateandtime_entry.get().strip()
    if (newJobExplanation == "") or (newJobDateAndTime == ""):
        Label(update_record, text="Error: Job Explanation or Job Date and Time cannot be null.", fg="red", font=("calibri",11)).pack()
        briefdescriptionofjob_entry.delete(0, END)
        selecteddateandtime_entry.delete(0, END)
    elif (len(newJobExplanation)>100) or (not is_valid_sqlite_datetime(newJobDateAndTime)):
        Label(update_record, text="Error: Job Explanation must be between 1 to 99 characters and Job Date and Time must be a valid date.", fg="red", font=("calibri",11)).pack()
        briefdescriptionofjob_entry.delete(0, END)
        selecteddateandtime_entry.delete(0, END)
    else:
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        qrySQLUpdate = "UPDATE Jobs SET JobDescription = ?, JobDateAndTime = ? WHERE JobID = ?"
        cursor.execute(qrySQLUpdate, (newJobExplanation, newJobDateAndTime, selectedJobID))

        conn.commit()
        conn.close()
        Label(update_record, text="Record successfully updated.",fg="green",font=("calibri, 11")).pack()
        briefdescriptionofjob_entry.delete(0, END)
        selecteddateandtime_entry.delete(0, END)

def updating_record(selectedJobID):
    global row_selected
    global update_record
    global main_screen
    global briefdescriptionofjob_entry
    global selecteddateandtime_entry
    row_selected.withdraw()
    update_record = Toplevel(main_screen)
    update_record.geometry("1280x720")
    update_record.title("Update Job Information (update_record)")
    Label(update_record, text="Update Job Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(update_record, text="Please update the fields below. All fields marked with an asterisk (*) are mandatory. The format for Selected Date and Time is YYYY-mm-dd HH:MM:SS.",).pack(pady=10)
    briefdescriptionofjob = StringVar()
    selecteddateandtime = StringVar()
    #Brief Description of Job
    briefdescriptionofjob_label = Label(update_record, text="Brief Description of Job *").pack()
    briefdescriptionofjob_entry = Entry(update_record, textvariable=briefdescriptionofjob)
    briefdescriptionofjob_entry.pack()
    #Selected Date and Time
    selecteddateandtime_label = Label(update_record, text="Selected Date and Time *").pack()
    selecteddateandtime_entry = Entry(update_record, textvariable=selecteddateandtime)
    selecteddateandtime_entry.pack(pady=5)
    Button(update_record, text="Change Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=lambda: change_record(selectedJobID)).pack()
    def updating_record_on_close():
        row_selected.deiconify()  # Show the main screen again
        update_record.destroy()

    update_record.protocol("WM_DELETE_WINDOW", updating_record_on_close)
    
def delete_record_on_close():
    global row_selected
    global delete_window
    row_selected.deiconify()
    delete_window.destroy()
    
def delete_job_info(selectedJobID):
    global delete_window
    global jobtree
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    try:
        qryDelete = "DELETE FROM Jobs WHERE JobID = ?"
        cursor.execute(qryDelete, (selectedJobID,))
        
        conn.commit()
        Label(delete_window, text="Record successfully deleted.", fg="green", font=("calibri", 11)).pack(pady=10)
        # Clear existing rows in the treeview
        for record in jobtree.get_children():
            jobtree.delete(record)
        jobinfo = GetJobInfo()
        for record in jobinfo:
            jobtree.insert("", 'end', values=record)

    except sqlite3.Error as e:
        conn.rollback()
        Label(delete_window, text=f"Database Error: {e}", fg="red", font=("calibri", 11)).pack()

    finally:
        conn.close()

def delete_record(selectedJobID):
    global delete_window
    global row_selected
    global main_screen
    row_selected.withdraw()
    delete_window = Toplevel(main_screen)
    delete_window.geometry("1280x720")
    delete_window.protocol("WM_DELETE_WINDOW", lambda: None)
    delete_window.title("Delete Job Information (delete_record)")
    Label(delete_window, text="Delete Job Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(delete_window, text="Please confirm deletion of the following job information.",).pack(pady=10)
    Label(delete_window, text="").pack()
    Button(delete_window, text="Yes", height="1", width="20", font=("Calibri", 13), command=lambda: delete_job_info(selectedJobID)).pack()
    Label(delete_window, text="").pack()
    Button(delete_window, text="No", height="1", width="20", font=("Calibri", 13), command=delete_record_on_close).pack()

def table_widget_row_selected(selectedJobID):
    global editjobinfo_window
    global row_selected
    global main_screen
    editjobinfo_window.withdraw()
    row_selected = Toplevel(main_screen)
    row_selected.geometry("1280x720")
    row_selected.title("Update/Delete Job Information (table_widget_row_selected(selectedJobID))")
    Label(row_selected, text="Update/Delete Job Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(row_selected, text="").pack()
    Button(row_selected, text="Update Record", width=30, height=1, command=lambda: updating_record(selectedJobID)).pack()
    Label(row_selected, text="").pack()
    Button(row_selected, text="Delete Record", width=30, height=1, command=lambda: delete_record(selectedJobID)).pack()
    Label(row_selected, text="").pack()
    def row_selected_on_close():
        editjobinfo_window.deiconify()  # Show the main screen again
        row_selected.destroy()

    row_selected.protocol("WM_DELETE_WINDOW", row_selected_on_close)
    
def on_row_select(event):
    global jobtree
    #Get the currently selected item IIDs
    selected_items = jobtree.selection()
    if selected_items:
        #Get the first selected item's IID
        selected_item_iid = selected_items[0]
        # Retrieve all values associated with that specific row's IID
        item_details = jobtree.item(selected_item_iid)
        # Extract just JobID from the list of values
        selectedJobID = item_details['values'][0] 
        # Call the next function with the JobID
        table_widget_row_selected(selectedJobID)

    
def GetJobInfo():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryJob = "SELECT * FROM Jobs"
    cursor.execute(qryJob)
    queryResult = cursor.fetchall()
    conn.close()
    return queryResult

def editjobinfo_on_close():
    staff_main_menu.deiconify()
    editjobinfo_window.destroy()
    
def EditJobInformation():
    global staff_main_menu
    global main_screen
    global editjobinfo_window
    global jobtree
    staff_main_menu.withdraw()
    editjobinfo_window = Toplevel(main_screen)
    editjobinfo_window.geometry("1280x720")
    editjobinfo_window.title("EditJobInformation")
    Label(editjobinfo_window, text="Edit Job Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(editjobinfo_window, text="Please choose a record below to edit.",).pack(pady=10)
    style = ttk.Style()
    # Configure the Treeview to show vertical lines
    style.configure("Treeview", font=("Calibri", 14), rowheight=30, background="white", foreground="black", fieldbackground="white")
    # Add a border to each cell/heading
    style.configure("Treeview.Heading", background="lightgray", font=("Calibri", 15, "bold"))
    columns = ("JobID", "CustomerID", "JobDescription", "JobDateAndTime")
    jobtree = ttk.Treeview(editjobinfo_window, columns=columns, show="headings")
    jobtree.heading("JobID", text="JobID")
    jobtree.heading("CustomerID", text="CustomerID")
    jobtree.heading("JobDescription", text="Job Description")
    jobtree.heading("JobDateAndTime", text="Job Date And Time")
    jobtree.column("JobID", width=25)
    jobtree.column("CustomerID", width=25)
    jobtree.column("JobDescription", width=400)
    jobtree.column("JobDateAndTime", width=150)
    jobinfo = GetJobInfo()
    for record in jobinfo:
        jobtree.insert("", tk.END, values=record)
    jobtree.pack(pady=20, fill=tk.BOTH, expand=True)
    jobtree.bind("<<TreeviewSelect>>", on_row_select)
    Button(editjobinfo_window, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=editjobinfo_on_close).pack()
    
def savequote():
    global quote_window
    global requestquoteid_entry
    global jobid_entry
    global customerid_entry
    global quoteestimatedprice_entry
    requestquoteid_info = requestquoteid_entry.get().strip()
    jobid_info = jobid_entry.get().strip()
    customerid_info = customerid_entry.get().strip()
    quoteestimatedprice_info = quoteestimatedprice_entry.get().strip()
    if (len(requestquoteid_info)==0):
        Label(quote_window, text="Error: RequestQuoteID cannot be null.", fg="red", font=("Calibri", 13)).pack()
        requestquoteid_entry.delete(0, END)
    elif (len(customerid_info)==0):
        Label(quote_window, text="Error: CustomerID cannot be null.", fg="red", font=("Calibri", 13)).pack()
        customerid_entry.delete(0, END)
    elif (len(quoteestimatedprice_info)==0):
        Label(quote_window, text="Error: QuoteEstimatedPrice cannot be null.", fg="red", font=("Calibri", 13)).pack()
        quoteestimatedprice_entry.delete(0, END)
    elif (not re.match(r'^\d{1,8}(\.\d{1,2})?$', quoteestimatedprice_info)):
        Label(quote_window, text="Error: Invalid price format. Use up to 8 digits and 2 decimals (e.g 123.45).", fg="red", font=("Calibri", 13)).pack()
        quoteestimatedprice_entry.delete(0, END)
    else:
        #Connect to database
        conn = sqlite3.connect('Backend.db')
        cursor = conn.cursor()
        #Query to check if the record exists in tblRequestQuotes using parameter queries (?) to prevent SQL injections
        qryFindRequestQuote = "SELECT * FROM RequestQuotes WHERE RequestQuoteID = ? AND CustomerID = ? AND JobID = ?"
        cursor.execute(qryFindRequestQuote, (requestquoteid_info, customerid_info, jobid_info))
        rq_record = cursor.fetchone()
        conn.close()
        #Validation to check if the record exists with those specific inputs, and if it exists save the generated quote to tblQuotes
        if rq_record is None:
            Label(quote_window, text="Error: IDs do not match any existing RequestQuotes record.", fg="red", font=("Calibri", 13)).pack()
            requestquoteid_entry.delete(0, END)
            customerid_entry.delete(0, END)
            jobid_entry.delete(0, END)
        else:
            quotedate = datetime.now()
            conn = sqlite3.connect("Backend.db")
            cursor = conn.cursor()
            qrySaveQuote = "INSERT INTO Quotes (RequestQuoteID, JobID, CustomerID, QuoteEstimatedPrice, QuoteDate) VALUES (?,?,?,?,?)"
            cursor.execute(qrySaveQuote,(requestquoteid_info,jobid_info,customerid_info,quoteestimatedprice_info,quotedate))
            
            conn.commit()
            conn.close()
            Label(quote_window, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
            requestquoteid_entry.delete(0, END)
            customerid_entry.delete(0, END)
            jobid_entry.delete(0, END)
            quoteestimatedprice_entry.delete(0, END)
            
            
            
        
    
def GetJobIDs():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryJobIDs = "SELECT JobID FROM Jobs"
    cursor.execute(qryJobIDs)
    JobIDResult = [row[0] for row in cursor.fetchall()] 
    conn.close()
    return JobIDResult

def generatequote():
    global staff_main_menu
    global main_screen
    global quote_window
    global requestquoteid_entry
    global jobid_entry
    global customerid_entry
    global quoteestimatedprice_entry
    staff_main_menu.withdraw()
    quote_window = Toplevel(main_screen)
    quote_window.geometry("1280x720")
    quote_window.title("Generate Quotes (frmQuotes)")
    Label(quote_window, text="Generate Quotes", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(quote_window, text="Please enter all details. All fields marked with an asterisk (*) are mandatory.",).pack(pady=10)
    requestquoteid = StringVar()
    get_jobids = GetJobIDs()
    jobid = StringVar()
    customerid = StringVar()
    quoteestimatedprice = StringVar()
    def fetch_from_db(*args):
        search_id = requestquoteid.get()
        if not search_id:
            jobid.set("") #Clear if ID empty
            customerid.set("")
        try:
            #Connect to database
            conn = sqlite3.connect("Backend.db")
            cursor = conn.cursor()
            
            #Query for the specific RequestQuoteID
            cursor.execute("SELECT JobID, CustomerID FROM RequestQuotes WHERE RequestQuoteID = ?", (search_id,))
            result = cursor.fetchone()
            
            #If found, autofill the other variables
            if result:
                jobid.set(result[0])
                customerid.set(result[1])
            else:
                jobid.set("") #Clear if ID not found
                customerid.set("")
                
            conn.close()
            
        except Exception as e:
            print(f"Database error: {e}")
    #Register the tracer to watch for any changes of the value of RequestQuoteID
    requestquoteid.trace_add("write", fetch_from_db)
    #RequestQuoteID
    requestquoteid_label = Label(quote_window, text="RequestQuoteID *").pack()
    requestquoteid_entry = Entry(quote_window, textvariable=requestquoteid)
    requestquoteid_entry.pack()
    #JobID
    jobid_label = Label(quote_window, text="JobID ").pack()
    jobid_entry = ttk.Combobox(
        quote_window, 
        textvariable=jobid, 
        values=get_jobids, 
        state="readonly"
    )
    jobid_entry.pack(pady=5)
    if get_jobids: # Check if the list is not empty before trying to set
        jobid_entry.set(get_jobids[0]) # Sets the first item as the default selection
    #CustomerID
    customerid_label = Label(quote_window, text="CustomerID *").pack()
    customerid_entry = Entry(quote_window, textvariable=customerid)
    customerid_entry.pack()
    #QuoteEstimatedPrice
    quoteestimatedprice_label = Label(quote_window, text="QuoteEstimatedPrice (£) *").pack()
    quoteestimatedprice_entry = Entry(quote_window, textvariable=quoteestimatedprice)
    quoteestimatedprice_entry.pack()
    Button(quote_window, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=savequote).pack()
    def generatequote_on_close():
        staff_main_menu.deiconify()  # Show the main screen again
        quote_window.destroy()

    quote_window.protocol("WM_DELETE_WINDOW", generatequote_on_close)
    
def saveinvoice():
    global invoice_window
    global Customerid_entry
    global quoteid_entry
    global Jobid_entry
    global invoiceprice_entry
    global invoicereason_entry
    global addextra_entry
    quoteid_info = quoteid_entry.get().strip()
    Customerid_info = Customerid_entry.get().strip()
    Jobid_info = Jobid_entry.get().strip()
    invoiceprice_info = invoiceprice_entry.get().strip()
    invoicereason_info = invoicereason_entry.get().strip()
    addextra_info = addextra_entry.get().strip()
    if len(quoteid_info)==0:
        Label(invoice_window, text="Error: QuoteID cannot be null.", fg="red", font=("Calibri",11)).pack()
        quoteid_entry.delete(0, END)
    elif len(Customerid_info)==0:
        Label(invoice_window, text="Error: CustomerID cannot be null.", fg="red", font=("Calibri",11)).pack()
        Customerid_entry.delete(0, END)
    elif len(Jobid_info)==0:
        Label(invoice_window, text="Error: JobID cannot be null.", fg="red", font=("Calibri",11)).pack()
        Jobid_entry.delete(0, END)
    elif (not re.match(r'^\d{1,8}(\.\d{1,2})?$', invoiceprice_info)):
        Label(invoice_window, text="Error: Invalid price format for InvoicePrice. Use up to 8 digits and 2 decimals (e.g 123.45).", fg="red", font=("Calibri",11)).pack()
        invoiceprice_entry.delete(0, END)
    elif (len(invoicereason_info)==0) or (len(invoicereason_info)>100):
        Label(invoice_window, text="Error: Invoice Reason must be between 1 and 100 characters long.", fg="red", font=("Calibri",11)).pack()
        invoicereason_entry.delete(0, END)
    elif (len(addextra_info)>0) and (not re.match(r'^\d{1,8}(\.\d{1,2})?$', addextra_info)):
        Label(invoice_window, text="Error: Invalid price format for AddExtra. Use up to 8 digits and 2 decimals (e.g 123.45).", fg="red", font=("Calibri",11)).pack()
        addextra_entry.delete(0, END)
    else:
        #Connect to database
        conn = sqlite3.connect('Backend.db')
        cursor = conn.cursor()
        #Query to check if the record exists in tblRequestQuotes using parameter queries (?) to prevent SQL injections
        qryFindQuote = "SELECT * FROM Quotes WHERE QuoteID = ? AND CustomerID = ? AND JobID = ?"
        cursor.execute(qryFindQuote, (quoteid_info, Customerid_info, Jobid_info))
        q_record = cursor.fetchone()
        conn.close()
        #Validation to check if the record exists with those specific inputs, and if it exists save the generated quote to tblQuotes
        if q_record is None:
            Label(invoice_window, text="Error: IDs do not match any existing RequestQuotes record.", fg="red", font=("Calibri", 13)).pack()
            quoteid_entry.delete(0, END)
            Customerid_entry.delete(0, END)
            Jobid_entry.delete(0, END)
        else:
            invoicedate = datetime.now()
            conn = sqlite3.connect("Backend.db")
            cursor = conn.cursor()
            qrySaveInvoice = "INSERT INTO Invoices (QuoteID,CustomerID,JobID,InvoicePrice,InvoiceReason,InvoiceExtraPrice,InvoiceDate) VALUES (?,?,?,?,?,?,?)"
            cursor.execute(qrySaveInvoice,(quoteid_info,Customerid_info,Jobid_info,invoiceprice_info,invoicereason_info,addextra_info,invoicedate))
            
            conn.commit()
            conn.close()
            Label(invoice_window, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
            quoteid_entry.delete(0, END)
            Customerid_entry.delete(0, END)
            Jobid_entry.delete(0, END)
            invoiceprice_entry.delete(0, END)
            invoicereason_entry.delete(0, END)
            addextra_entry.delete(0, END)
            
def generateinvoice():
    global staff_main_menu
    global main_screen
    global invoice_window
    global quoteid_entry
    global Jobid_entry
    global Customerid_entry
    global invoiceprice_entry
    global invoicereason_entry
    global addextra_entry
    staff_main_menu.withdraw()
    invoice_window = Toplevel(main_screen)
    invoice_window.geometry("1280x720")
    invoice_window.title("Generate Invoices (frmNewInvoice)")
    Label(invoice_window, text="Generate Invoices", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(invoice_window, text="Please enter all details. All fields marked with an asterisk (*) are mandatory.",).pack(pady=10)
    quoteid = StringVar()
    getalljobs = GetJobIDs()
    Jobid = StringVar()
    Customerid = StringVar()
    invoiceprice = StringVar()
    invoicereason = StringVar()
    addextra = StringVar()
    def fetch_from_database(*args):
        search_id = quoteid.get()
        if not search_id:
            Jobid.set("") #Clear if ID empty
            Customerid.set("")
        try:
            #Connect to database
            conn = sqlite3.connect("Backend.db")
            cursor = conn.cursor()
            
            #Query for the specific QuoteID
            cursor.execute("SELECT JobID, CustomerID FROM Quotes WHERE QuoteID = ?", (search_id,))
            result = cursor.fetchone()
            
            #If found, autofill the other variables
            if result:
                Jobid.set(result[0])
                Customerid.set(result[1])
            else:
                Jobid.set("") #Clear if ID not found
                Customerid.set("")
                
            conn.close()
            
        except Exception as e:
            print(f"Database error: {e}")
    #Register the tracer to watch for any changes of the value of QuoteID
    quoteid.trace_add("write", fetch_from_database)
    #QuoteID
    quoteid_label = Label(invoice_window, text="QuoteID *").pack()
    quoteid_entry = Entry(invoice_window, textvariable=quoteid)
    quoteid_entry.pack()
    #JobID
    Jobid_label = Label(invoice_window, text="JobID *").pack()
    Jobid_entry = ttk.Combobox(invoice_window, textvariable=Jobid, values=getalljobs, state="readonly")
    Jobid_entry.pack(pady=5)
    if getalljobs: # Check if the list is not empty before trying to set
        Jobid_entry.set(getalljobs[0]) # Sets the first item as the default selection
    #CustomerID
    Customerid_label = Label(invoice_window, text="CustomerID *").pack()
    Customerid_entry = Entry(invoice_window, textvariable=Customerid)
    Customerid_entry.pack()
    #InvoicePrice
    invoiceprice_label = Label(invoice_window, text="InvoicePrice (£) *").pack()
    invoiceprice_entry = Entry(invoice_window, textvariable=invoiceprice)
    invoiceprice_entry.pack()
    #InvoiceReason
    invoicereason_label = Label(invoice_window, text="InvoiceReason *").pack()
    invoicereason_entry = Entry(invoice_window, textvariable=invoicereason)
    invoicereason_entry.pack()
    #AddExtra
    addextra_label = Label(invoice_window, text="AddExtra (£)").pack()
    addextra_entry = Entry(invoice_window, textvariable=addextra)
    addextra_entry.pack()
    Button(invoice_window, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=saveinvoice).pack()
    def generateinvoice_on_close():
        staff_main_menu.deiconify()  # Show the main screen again
        invoice_window.destroy()

    invoice_window.protocol("WM_DELETE_WINDOW", generateinvoice_on_close)

def save_record(selectedGuaranteeID):
    global guaranteerow_selected
    global approvedeny_entry
    newApproveDeny = approvedeny_entry.get().strip()
    if newApproveDeny == "Approved":
        is_approved = True
    elif newApproveDeny == "Denied":
        is_approved = False
    else:
        Label(guaranteerow_selected, text="Error: Invalid input. Approve/Deny can only be Approved or Denied.", fg="red", font=("calibri", 11)).pack()
        approvedeny_entry.delete(0, END)

    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryUpdate = "UPDATE Guarantees SET GuaranteeApprovedOrDenied = ? WHERE GuaranteeID = ?"
    
    cursor.execute(qryUpdate, (is_approved, selectedGuaranteeID)) 
    
    conn.commit()
    conn.close()
    Label(guaranteerow_selected, text="Record successfully updated.", fg="green", font=("calibri", 11)).pack()
    approvedeny_entry.delete(0, END)


def guarantee_widget_row_selected(selectedGuaranteeID):
    global guaranteerow_selected
    global guarantee_window
    global main_screen
    global briefdescriptionofjob_entry
    global selecteddateandtime_entry
    global approvedeny_entry
    guarantee_window.withdraw()
    guaranteerow_selected = Toplevel(main_screen)
    guaranteerow_selected.geometry("1280x720")
    guaranteerow_selected.title("Approve/Deny Selected Guarantee (guarantee_widget_row_selected(selectedGuaranteeID))")
    Label(guaranteerow_selected, text="Approve/Deny Selected Guarantee", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(guaranteerow_selected, text="Please update the fields below. All fields marked with an asterisk (*) are mandatory. A guarantee can either be Approved or Denied.",).pack(pady=10)
    approvedeny = StringVar()
    #Approve/Deny
    approvedeny_label = Label(guaranteerow_selected, text="Approve/Deny *").pack()
    approvedeny_entry = Entry(guaranteerow_selected, textvariable=approvedeny)
    approvedeny_entry.pack()
    Button(guaranteerow_selected, text="Change Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=lambda: save_record(selectedGuaranteeID)).pack()
    def guarantee_row_selected_on_close():
        guarantee_window.deiconify()  # Show the main screen again
        guaranteerow_selected.destroy()

    guaranteerow_selected.protocol("WM_DELETE_WINDOW", guarantee_row_selected_on_close)
    
def on_guarantee_select(event):
    global guaranteetree
    #Get the currently selected item IIDs
    selected_items = guaranteetree.selection()
    if selected_items:
        #Get the first selected item's IID
        selected_item_iid = selected_items[0]
        # Retrieve all values associated with that specific row's IID
        item_details = guaranteetree.item(selected_item_iid)
        # Extract just GuaranteeID from the list of values
        selectedGuaranteeID = item_details['values'][0] 
        # Call the next function with the GuaranteeID
        guarantee_widget_row_selected(selectedGuaranteeID)
        
def approvedenyguarantee_on_close():
    staff_main_menu.deiconify()  # Show the main screen again
    guarantee_window.destroy()

def GetGuaranteeInfo():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryGuarantees = "SELECT * FROM Guarantees"
    cursor.execute(qryGuarantees)
    guaranteeResult = cursor.fetchall()
    conn.close()
    return guaranteeResult
    
def approvedenyguarantee():
    global staff_main_menu
    global main_screen
    global guarantee_window
    global guaranteetree
    staff_main_menu.withdraw()
    guarantee_window = Toplevel(main_screen)
    guarantee_window.geometry("1280x720")
    guarantee_window.title("Approve/Deny Guarantee")
    Label(guarantee_window, text="Approve/Deny Guarantee", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(guarantee_window, text="Please choose a record below to edit.",).pack(pady=10)
    style = ttk.Style()
    # Configure the Treeview to show vertical lines
    style.configure("Treeview", font=("Calibri", 14), rowheight=30, background="white", foreground="black", fieldbackground="white")
    # Add a border to each cell/heading
    style.configure("Treeview.Heading", background="lightgray", font=("Calibri", 15, "bold"))
    columns = ("GuaranteeID", "JobID", "CustomerID", "GuaranteeMessage", "GuaranteeApprovedOrDenied", "GuaranteeDate")
    guaranteetree = ttk.Treeview(guarantee_window, columns=columns, show="headings")
    guaranteetree.heading("GuaranteeID", text="GuaranteeID")
    guaranteetree.heading("JobID", text="JobID")
    guaranteetree.heading("CustomerID", text="CustomerID")
    guaranteetree.heading("GuaranteeMessage", text="GuaranteeMessage")
    guaranteetree.heading("GuaranteeApprovedOrDenied", text="ApprovedOrDenied")
    guaranteetree.heading("GuaranteeDate", text="GuaranteeDate")
    guaranteetree.column("GuaranteeID", width=75, anchor="center")
    guaranteetree.column("JobID", width=75, anchor="center")
    guaranteetree.column("CustomerID", width=100, anchor="center")
    guaranteetree.column("GuaranteeMessage", width=400)
    guaranteetree.column("GuaranteeApprovedOrDenied", width=150)
    guaranteetree.column("GuaranteeDate", width=150)
    guaranteeinfo = GetGuaranteeInfo()
    for row in guaranteeinfo:
        guaranteetree.insert("", "end", values=row)
    guaranteetree.pack(pady=20, fill=tk.BOTH, expand=True)
    guaranteetree.bind("<<TreeviewSelect>>", on_guarantee_select)
    Button(guarantee_window, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=approvedenyguarantee_on_close).pack()

def staffmainmenu():
    global staff_main_menu
    global main_screen
    global login_screen
    login_screen.withdraw()
    staff_main_menu = Toplevel(main_screen)
    staff_main_menu.geometry("1280x720")
    staff_main_menu.title("Staff Main Menu")
    Label(staff_main_menu, text="Staff Main Menu", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(staff_main_menu, text="Please click on the relevant option you would like to use in the program.",).pack(pady=10)
    Button(staff_main_menu, text="Update/Edit/Delete Job Information", width=30, height=1, command=EditJobInformation).pack()
    Label(staff_main_menu, text="").pack()
    Button(staff_main_menu, text="Generate Quotes", width=30, height=1, command=generatequote).pack()
    Label(staff_main_menu, text="").pack()
    Button(staff_main_menu, text="Generate Invoices", width=30, height=1, command=generateinvoice).pack()
    Label(staff_main_menu, text="").pack()
    Button(staff_main_menu, text="Approve/Deny One-Year Guarantees", width=30, height=1, command=approvedenyguarantee).pack()
    Label(staff_main_menu, text="").pack()
    Button(staff_main_menu, text="Access Customer Main Menu", width=30, height=1, command=customermainmenu).pack()
    Label(staff_main_menu, text="").pack()
    Button(staff_main_menu, text="Logout", width=30, height=1, command=logout).pack()

def delete_customer_info(selectedCustomerID):
    global delete_customer_window
    global customertree
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    try:
        qryCustomerDelete = "DELETE FROM Customers WHERE CustomerID = ?"
        cursor.execute(qryCustomerDelete, (selectedCustomerID,))
        
        conn.commit()
        Label(delete_customer_window, text="Record successfully deleted.", fg="green", font=("calibri", 11)).pack(pady=10)
        # Clear existing rows in the treeview
        for record in customertree.get_children():
            customertree.delete(record)
        customerinfo = GetCustomerInfo()
        for record in customerinfo:
            customertree.insert("", 'end', values=record)

    except sqlite3.Error as e:
        conn.rollback()
        Label(delete_customer_window, text=f"Database Error: {e}", fg="red", font=("calibri", 11)).pack()

    finally:
        conn.close()
        
def delete_customer_record_on_close():
    global delete_customer_window
    global editcustomerinfo_window
    editcustomerinfo_window.deiconify()
    delete_customer_window.destroy()

def delete_customer_record(selectedCustomerID):
    global delete_customer_window
    global editcustomerinfo_window
    global main_screen
    editcustomerinfo_window.withdraw()
    delete_customer_window = Toplevel(main_screen)
    delete_customer_window.protocol("WM_DELETE_WINDOW", lambda: None)
    delete_customer_window.geometry("1280x720")
    delete_customer_window.title("Delete Customer Information")
    Label(delete_customer_window, text="Delete Customer Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(delete_customer_window, text="Please confirm deletion of the following customer information.",).pack(pady=10)
    Label(delete_customer_window, text="").pack()
    Button(delete_customer_window, text="Yes", height="1", width="20", font=("Calibri", 13), command=lambda: delete_customer_info(selectedCustomerID)).pack()
    Label(delete_customer_window, text="").pack()
    Button(delete_customer_window, text="No", height="1", width="20", font=("Calibri", 13), command=delete_customer_record_on_close).pack()
    
def change_customer_record(selectedCustomerID):
    global update_customer_record_window
    global CustomerUsername_entry, CustomerPassword_entry, CustomerFirstname_entry, CustomerLastname_entry, CustomerEmailAddress_entry, CustomerPhoneNumber_entry, CustomerHouseAddress_entry, CustomerPostcode_entry
    u_info = CustomerUsername_entry.get().strip()
    p_info = CustomerPassword_entry.get().strip()
    f_info = CustomerFirstname_entry.get().strip()
    l_info = CustomerLastname_entry.get().strip()
    e_info = CustomerEmailAddress_entry.get().strip()
    ph_info = CustomerPhoneNumber_entry.get().strip()
    h_info = CustomerHouseAddress_entry.get().strip()
    pc_info = CustomerPostcode_entry.get().strip()

    # This dictionary stores only the valid data to be updated
    updates = {}
    
    #Username
    if u_info != "":
        if len(u_info) < 5 or len(u_info) > 40:
            Label(update_customer_record_window, text="Error: Username must be between 5 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
            CustomerUsername_entry.delete(0, END)
            return
        updates["CustomerUsername"] = u_info

    # Password
    if p_info != "":
        if len(p_info) < 8 or len(p_info) > 40:
            Label(update_customer_record_window, text="Error: Password must be between 8 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
            CustomerPassword_entry.delete(0, END)
            return
        updates["CustomerPassword"] = hash_password(p_info)

    # Firstname
    if f_info != "":
        if len(f_info) > 50:
            Label(update_customer_record_window, text="Error: First Name must be between 1 and 50 characters long.", fg="red", font=("calibri", 11)).pack()
            CustomerFirstName_entry.delete(0, END)
            return
        updates["CustomerFirstName"] = f_info

    # Lastname
    if l_info != "":
        updates["CustomerSurname"] = l_info

    # Email Address
    if e_info != "":
        if len(e_info) > 100 or "@" not in e_info or "." not in e_info:
            Label(update_customer_record_window, text="Error: Invalid email format.", fg="red", font=("calibri", 11)).pack()
            CustomerEmailAddress_entry.delete(0, END)
            return
        updates["CustomerEmailAddress"] = e_info

    # Phone Number
    if ph_info != "":
        if not ph_info.isdigit():
            Label(update_customer_record_window, text="Error: Phone Number must be numerical.", fg="red", font=("calibri", 11)).pack()
            CustomerPhoneNumber_entry.delete(0, END)
            return
        updates["CustomerPhoneNumber"] = ph_info

    # House Address
    if h_info != "":
        if len(h_info) > 100:
            Label(update_customer_record_window, text="Error: House Address must be between 1 and 100 characters.", fg="red", font=("calibri", 11)).pack()
            CustomerHouseAddress_entry.delete(0, END)
            return
        updates["CustomerHouseAddress"] = h_info

    # Postcode
    if pc_info != "":
        if len(pc_info) > 20:
            Label(update_customer_record_window, text="Error: Postcode too long.", fg="red", font=("calibri", 11)).pack()
            CustomerPostcode_entry.delete(0, END)
            return
        updates["CustomerPostcode"] = pc_info

    #Check if anything actually changed
    if not updates:
        Label(update_customer_record_window, text="Unchanged: No changes detected.", fg="orange", font=("calibri", 11)).pack()
        return

    #Connect to database
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    
    #Check if username is taken and only if they are trying to change it
    if "CustomerUsername" in updates:
        cursor.execute("SELECT * FROM Customers WHERE CustomerUsername = ? AND CustomerID != ?", (u_info, selectedCustomerID))
        if cursor.fetchone():
            Label(update_customer_record_window, text="Error: Username already exists.", fg="red", font=("calibri", 11)).pack()
            conn.close()
            return

    #Build and execute dynamic query
    set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
    values = list(updates.values())
    values.append(selectedCustomerID)
    
    cursor.execute(f"UPDATE Customers SET {set_clause} WHERE CustomerID = ?", tuple(values))
    
    conn.commit()
    conn.close()
    Label(update_customer_record_window, text="Record successfully updated.", fg="green", font=("calibri", 11)).pack()
    CustomerUsername_entry.delete(0, END)
    CustomerPassword_entry.delete(0, END)
    CustomerFirstName_entry.delete(0, END)
    CustomerSurname_entry.delete(0, END)
    CustomerEmailAddress_entry.delete(0, END)
    CustomerPhoneNumber_entry.delete(0, END)
    CustomerHouseAddress_entry.delete(0, END)
    CustomerPostcode_entry.delete(0, END)
    
def update_customer_record(selectedCustomerID):
    global update_customer_record_window
    global editcustomerinfo_window
    global main_screen
    global CustomerUsername_entry, CustomerPassword_entry, CustomerFirstname_entry, CustomerLastname_entry, CustomerEmailAddress_entry, CustomerPhoneNumber_entry, CustomerHouseAddress_entry, CustomerPostcode_entry
    editcustomerinfo_window.withdraw()

    update_customer_record_window = Toplevel(main_screen)
    update_customer_record_window.title("Update Customer Information")
    
    update_customer_record_window.geometry("1280x720")

    # Tkinter variables
    CustomerUsername = StringVar()
    CustomerPassword = StringVar()
    CustomerFirstname = StringVar()
    CustomerLastname = StringVar()
    CustomerEmailAddress = StringVar()
    CustomerPhoneNumber = StringVar()
    CustomerHouseAddress = StringVar()
    CustomerPostcode = StringVar()

    # Instruction label
    Label(update_customer_record_window, text="Update Customer Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(update_customer_record_window, text="Please enter information into the fields below to update the customer's information. "
    "Any fields left blank will not be updated and will remain the same.",).pack(pady=10)
    #Username
    CustomerUsername_label = Label(update_customer_record_window, text="Username ").pack()
    CustomerUsername_entry = Entry(update_customer_record_window, textvariable=CustomerUsername)
    CustomerUsername_entry.pack()
    #Password
    CustomerPassword_label = Label(update_customer_record_window, text="Password ").pack()
    CustomerPassword_entry = Entry(update_customer_record_window, textvariable=CustomerPassword, show="*")
    CustomerPassword_entry.pack()
    #Firstname
    CustomerFirstname_label = Label(update_customer_record_window, text="First Name ").pack()
    CustomerFirstname_entry = Entry(update_customer_record_window, textvariable=CustomerFirstname)
    CustomerFirstname_entry.pack()
    #Lastname
    CustomerLastname_label = Label(update_customer_record_window, text="Last Name ").pack()
    CustomerLastname_entry = Entry(update_customer_record_window, textvariable=CustomerLastname)
    CustomerLastname_entry.pack()
    #Emailaddress
    CustomerEmailAddress_label = Label(update_customer_record_window, text="Email Address ").pack()
    CustomerEmailAddress_entry = Entry(update_customer_record_window, textvariable=CustomerEmailAddress)
    CustomerEmailAddress_entry.pack()
    #Phonenumber
    CustomerPhoneNumber_label = Label(update_customer_record_window, text="Phone Number ").pack()
    CustomerPhoneNumber_entry = Entry(update_customer_record_window, textvariable=CustomerPhoneNumber)
    CustomerPhoneNumber_entry.pack()
    #Houseaddress
    CustomerHouseAddress_label = Label(update_customer_record_window, text="House Address ").pack()
    CustomerHouseAddress_entry = Entry(update_customer_record_window, textvariable=CustomerHouseAddress)
    CustomerHouseAddress_entry.pack()
    #Postcode
    CustomerPostcode_label = Label(update_customer_record_window, text="Postcode ").pack()
    CustomerPostcode_entry = Entry(update_customer_record_window, textvariable=CustomerPostcode)
    CustomerPostcode_entry.pack()
    #create Update Record button
    Button(update_customer_record_window, text="Update Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=lambda: change_customer_record(selectedCustomerID)).pack()
    def update_customer_record_window_on_close():
        editcustomerinfo_window.deiconify()  # Show the main screen again
        update_customer_record_window.destroy()

    update_customer_record_window.protocol("WM_DELETE_WINDOW", update_customer_record_window_on_close)
    
def customer_widget_row_selected(selectedCustomerID):
    global editcustomerinfo_window
    global customer_window
    global main_screen
    customer_window.withdraw()
    editcustomerinfo_window = Toplevel(main_screen)
    editcustomerinfo_window.geometry("1280x720")
    editcustomerinfo_window.title("Update/Delete Customer Information (customer_widget_row_selected(selectedCustomerID))")
    Label(editcustomerinfo_window, text="Update/Delete Customer Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(editcustomerinfo_window, text="").pack()
    Button(editcustomerinfo_window, text="Update Record", width=30, height=1, command=lambda: update_customer_record(selectedCustomerID)).pack()
    Label(editcustomerinfo_window, text="").pack()
    Button(editcustomerinfo_window, text="Delete Record", width=30, height=1, command=lambda: delete_customer_record(selectedCustomerID)).pack()
    Label(editcustomerinfo_window, text="").pack()
    def editcustomerinfo_window_on_close():
        customer_window.deiconify()  # Show the main screen again
        editcustomerinfo_window.destroy()

    editcustomerinfo_window.protocol("WM_DELETE_WINDOW", editcustomerinfo_window_on_close)

def on_customer_select(event):
    global customertree
    #Get the currently selected item IIDs
    selected_items = customertree.selection()
    if selected_items:
        #Get the first selected item's IID
        selected_item_iid = selected_items[0]
        # Retrieve all values associated with that specific row's IID
        item_details = customertree.item(selected_item_iid)
        # Extract just CustomerID from the list of values
        selectedCustomerID = item_details['values'][0] 
        # Call the next function with the CustomerID
        customer_widget_row_selected(selectedCustomerID)
        
def GetCustomerInfo():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryCustomers = "SELECT * FROM Customers"
    cursor.execute(qryCustomers)
    customerResult = cursor.fetchall()
    conn.close()
    return customerResult

def EditCustomerInformation_on_close():
    global main_staff_main_menu
    global customer_window
    main_staff_main_menu.deiconify()
    customer_window.destroy()

def EditCustomerInformation():
    global main_staff_main_menu
    global main_screen
    global customer_window
    global customertree
    main_staff_main_menu.withdraw()
    customer_window = Toplevel(main_screen)
    customer_window.geometry("1280x720")
    customer_window.title("Update/Edit/Delete Customer Information (EditCustomerInformation())")
    Label(customer_window, text="Update/Edit/Delete Customer Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(customer_window, text="Please choose a record below in the table to edit.",).pack(pady=10)
    style = ttk.Style()
    style.configure("Treeview", font=("Calibri", 14), rowheight=30, background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", background="lightgray", font=("Calibri", 15, "bold"))
    columns = ("CustomerID", "CustomerUsername", "CustomerPassword", "CustomerFirstName", "CustomerSurname", "CustomerEmailAddress", "CustomerPhoneNumber", "CustomerHouseAddress", "CustomerPostcode")
    customertree = ttk.Treeview(customer_window, columns=columns, show="headings")
    customertree.heading("CustomerID", text="CustomerID")
    customertree.heading("CustomerUsername", text="Username")
    customertree.heading("CustomerPassword", text="Password")
    customertree.heading("CustomerFirstName", text="First Name")
    customertree.heading("CustomerSurname", text="Surname")
    customertree.heading("CustomerEmailAddress", text="Email Address")
    customertree.heading("CustomerPhoneNumber", text="Phone Number")
    customertree.heading("CustomerHouseAddress", text="House Address")
    customertree.heading("CustomerPostcode", text="Postcode")
    customertree.column("CustomerID", width=100, anchor="center")
    customertree.column("CustomerUsername", width=120)
    customertree.column("CustomerPassword", width=100) #hashed password
    customertree.column("CustomerFirstName", width=80)
    customertree.column("CustomerSurname", width=80)
    customertree.column("CustomerEmailAddress", width=220)
    customertree.column("CustomerPhoneNumber", width=80)
    customertree.column("CustomerHouseAddress", width=80)
    customertree.column("CustomerPostcode", width=80)
    customerinfo = GetCustomerInfo()
    for row in customerinfo:
        customertree.insert("", "end", values=row)
        
    customertree.pack(pady=20, fill=tk.BOTH, expand=True)
    customertree.bind("<<TreeviewSelect>>", on_customer_select)
    Button(customer_window, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=EditCustomerInformation_on_close).pack()

def addstaffaccount():
    global staffusername_entry
    global staffpassword_entry
    global addnewstaff_screen
    staffusername_info = staffusername_entry.get().strip()
    staffpassword_info = staffpassword_entry.get().strip()
    if (len(staffusername_info) == 0) or (len(staffpassword_info) == 0):
        Label(addnewstaff_screen, text="Error: Username and password must not be empty.", fg="red", font=("calibri", 11)).pack()
        staffusername_entry.delete(0, END)
        staffpassword_entry.delete(0, END)
    elif (len(staffusername_info) < 5) or (len(staffusername_info) > 40):
        Label(addnewstaff_screen, text="Error: Username must be between 5 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
        staffusername_entry.delete(0, END)
    elif (len(staffpassword_info) < 8) or (len(staffpassword_info) > 40):
        Label(addnewstaff_screen, text="Error: Password must be between 8 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
        staffpassword_entry.delete(0, END)
    else:
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        password1 = hash_password(staffpassword_info)
        insertStaffData = "INSERT INTO Staff(StaffUsername, StaffPassword) VALUES (?,?)"
        query = "SELECT * FROM Staff WHERE StaffUsername = ?"
        cursor.execute(query, (staffusername_info,))
        result = cursor.fetchone()
        if result:
            Label(addnewstaff_screen, text="Error: Username already exists.", fg="red", font=("calibri", 11)).pack()
            staffusername_entry.delete(0, END)
        else:
            cursor.execute(insertStaffData, (staffusername_info, password1))
            
            conn.commit()
            conn.close()
            Label(addnewstaff_screen, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
            staffusername_entry.delete(0, END)
            staffpassword_entry.delete(0, END)

def createstaffaccount():
    global main_staff_main_menu
    global main_screen
    global addnewstaff_screen
    global staffusername_entry
    global staffpassword_entry
    main_staff_main_menu.withdraw()
    addnewstaff_screen = Toplevel(main_screen)
    addnewstaff_screen.geometry("1280x720")
    addnewstaff_screen.title("Create Other Staff Accounts (createstaffaccount())")
    Label(addnewstaff_screen, text="Create Other Staff Accounts", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(addnewstaff_screen, text="Please enter all details below. All fields marked with an asterisk (*) are mandatory.",).pack(pady=10)
    staffusername = StringVar()
    staffpassword = StringVar()
    #StaffUsername
    staffusername_label = Label(addnewstaff_screen, text="StaffUsername *").pack()
    staffusername_entry = Entry(addnewstaff_screen, textvariable=staffusername)
    staffusername_entry.pack()
    #StaffPassword
    staffpassword_label = Label(addnewstaff_screen, text="StaffPassword *").pack()
    staffpassword_entry = Entry(addnewstaff_screen, textvariable=staffpassword, show="*")
    staffpassword_entry.pack()
    Button(addnewstaff_screen, text="Save Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=addstaffaccount).pack()
    def createstaffaccount_on_close():
        main_staff_main_menu.deiconify()  # Show the main screen again
        addnewstaff_screen.destroy()

    addnewstaff_screen.protocol("WM_DELETE_WINDOW", createstaffaccount_on_close)

def delete_staff_information(selectedStaffID):
    global deletestaff_window
    global stafftree
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    try:
        qryStaffDelete = "DELETE FROM Staff WHERE StaffID = ?"
        cursor.execute(qryStaffDelete, (selectedStaffID,))
        
        conn.commit()
        Label(deletestaff_window, text="Record successfully deleted.", fg="green", font=("calibri", 11)).pack(pady=10)
        # Clear existing rows in the treeview
        for record in stafftree.get_children():
            stafftree.delete(record)
        staffinfo = GetStaffInfo()
        for record in staffinfo:
            stafftree.insert("", 'end', values=record)

    except sqlite3.Error as e:
        conn.rollback()
        Label(deletestaff_window, text=f"Database Error: {e}", fg="red", font=("calibri", 11)).pack()

    finally:
        conn.close()

def delete_record_on_close():
    global deletestaffinfo_window
    global deletestaff_window
    deletestaffinfo_window.deiconify()  # Show the main screen again
    deletestaff_window.destroy()
    
def deletestaffinfo(selectedStaffID):
    global deletestaff_window
    global deletestaffinfo_window
    global main_screen
    deletestaffinfo_window.withdraw()
    deletestaff_window = Toplevel(main_screen)
    deletestaff_window.protocol("WM_DELETE_WINDOW", lambda: None)
    deletestaff_window.geometry("1280x720")
    deletestaff_window.title("Delete Staff Information (deletestaffinfo(selectedStaffID))")
    Label(deletestaff_window, text="Delete Staff Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(deletestaff_window, text="Please confirm deletion of the following staff information.",).pack(pady=10)
    Label(deletestaff_window, text="").pack()
    Button(deletestaff_window, text="Yes", height="1", width="20", font=("Calibri", 13), command=lambda: delete_staff_information(selectedStaffID)).pack()
    Label(deletestaff_window, text="").pack()
    Button(deletestaff_window, text="No", height="1", width="20", font=("Calibri", 13), command=delete_record_on_close).pack()

def on_staff_select(event):
    global stafftree
    #Get the currently selected item IIDs
    selected_items = stafftree.selection()
    if selected_items:
        #Get the first selected item's IID
        selected_item_iid = selected_items[0]
        # Retrieve all values associated with that specific row's IID
        item_details = stafftree.item(selected_item_iid)
        # Extract just StaffID from the list of values
        selectedStaffID = item_details['values'][0] 
        # Call the next function with the StaffID
        deletestaffinfo(selectedStaffID)

    
def GetStaffInfo():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryStaff = "SELECT * FROM Staff"
    cursor.execute(qryStaff)
    queryStaffResult = cursor.fetchall()
    conn.close()
    return queryStaffResult

def editstaffinfo_on_close():
    main_staff_main_menu.deiconify()
    deletestaffinfo_window.destroy()
    
def DeleteStaffInformation():
    global main_staff_main_menu
    global main_screen
    global deletestaffinfo_window
    global stafftree
    main_staff_main_menu.withdraw()
    deletestaffinfo_window = Toplevel(main_screen)
    deletestaffinfo_window.geometry("1280x720")
    deletestaffinfo_window.title("EditJobInformation")
    Label(deletestaffinfo_window, text="Delete Staff Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(deletestaffinfo_window, text="Please choose a record below to delete.",).pack(pady=10)
    style = ttk.Style()
    # Configure the Treeview to show vertical lines
    style.configure("Treeview", font=("Calibri", 14), rowheight=30, background="white", foreground="black", fieldbackground="white")
    # Add a border to each cell/heading
    style.configure("Treeview.Heading", background="lightgray", font=("Calibri", 15, "bold"))
    columns = ("StaffID", "StaffUsername", "StaffPassword")
    stafftree = ttk.Treeview(deletestaffinfo_window, columns=columns, show="headings")
    stafftree.heading("StaffID", text="StaffID")
    stafftree.heading("StaffUsername", text="StaffUsername")
    stafftree.heading("StaffPassword", text="StaffPassword")
    stafftree.column("StaffID", width=25)
    stafftree.column("StaffUsername", width=400)
    stafftree.column("StaffPassword", width=400)
    staffinfo = GetStaffInfo()
    for record in staffinfo:
        stafftree.insert("", tk.END, values=record)
    stafftree.pack(pady=20, fill=tk.BOTH, expand=True)
    stafftree.bind("<<TreeviewSelect>>", on_staff_select)
    Button(deletestaffinfo_window, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=editstaffinfo_on_close).pack()

def get_invoices_by_day(current_date):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    query = """SELECT InvoiceID, CustomerID, JobID, QuoteID, InvoicePrice, 
               InvoiceExtraPrice, InvoiceDate FROM Invoices 
               WHERE InvoiceDate = ?"""
    cursor.execute(query, (current_date,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_invoices_by_week(current_date):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    # strftime is used here for SQLite compatibility
    query = """SELECT InvoiceID, CustomerID, JobID, QuoteID, InvoicePrice, 
               InvoiceExtraPrice, InvoiceDate FROM Invoices 
               WHERE strftime('%W', InvoiceDate) = strftime('%W', ?) 
               AND strftime('%Y', InvoiceDate) = strftime('%Y', ?)"""
    cursor.execute(query, (current_date, current_date))
    results = cursor.fetchall()
    conn.close()
    return results

def get_invoices_by_month(current_date):
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    query = """SELECT InvoiceID, CustomerID, JobID, QuoteID, InvoicePrice, 
               InvoiceExtraPrice, InvoiceDate FROM Invoices 
               WHERE strftime('%m', InvoiceDate) = strftime('%m', ?) 
               AND strftime('%Y', InvoiceDate) = strftime('%Y', ?)"""
    cursor.execute(query, (current_date, current_date))
    results = cursor.fetchall()
    conn.close()
    return results

def create_combined_report_pdf(current_date, day_data, week_data, month_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Invoice Totals Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {current_date}", ln=True, align='C')
    pdf.ln(10)

    # Calculate Totals
    total_day = sum(float(row[4]) + float(row[5] or 0) for row in day_data)
    total_week = sum(float(row[4]) + float(row[5] or 0) for row in week_data)
    total_month = sum(float(row[4]) + float(row[5] or 0) for row in month_data)

    # Totals Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total Earned Today: GBP {total_day:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total Earned This Week: GBP {total_week:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total Earned This Month: GBP {total_month:,.2f}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Daily Records List
    pdf.cell(0, 10, "DAILY INVOICE RECORDS:", ln=True)
    pdf.set_font("Arial", size=10)
    for record in day_data:
        pdf.cell(0, 7, f"Invoice ID: {record[0]} | Price: £{record[4]:.2f} | Extra: £{record[5]:.2f}", ln=True)

    filename = "Invoice_Totals_Report.pdf"
    pdf.output(filename)
    return filename

def total_invoices_by_period():
    global main_screen
    global invoice_report_screen
    global main_staff_main_menu
    main_staff_main_menu.withdraw() # Hide the main menu

    invoice_report_screen = Toplevel(main_screen)
    invoice_report_screen.geometry("1280x720")
    invoice_report_screen.title("Total Invoices by Day, Week and Month (get_invoices_by_period())")

    # Header Label
    Label(invoice_report_screen, text="Total Invoices by Day, Week and Month", bg="blue", 
          width="300", height="2", font=("Calibri", 13)).pack()
    
    Label(invoice_report_screen, text="Processing records and generating PDF...", font=("Calibri", 11)).pack(pady=20)

    # Data Retrieval
    current_date = datetime.now().strftime('%Y-%m-%d')
    day_invoices = get_invoices_by_day(current_date)
    week_invoices = get_invoices_by_week(current_date)
    month_invoices = get_invoices_by_month(current_date)

    if day_invoices or week_invoices or month_invoices:
        # Generate the PDF
        pdf_filename = create_combined_report_pdf(current_date, day_invoices, week_invoices, month_invoices)
        
        # Show Success and Open File
        messagebox.showinfo("Success", f"PDF report generated: {pdf_filename}")
        os.startfile(pdf_filename)
        
        Label(invoice_report_screen, text=f"File saved as: {pdf_filename}", fg="green").pack()
    else:
        messagebox.showwarning("No Data", "No invoice records found for the current periods.")

    # Handle Closing the Window
    def get_invoices_by_period_on_close():
        main_staff_main_menu.deiconify() # Bring back the main menu
        invoice_report_screen.destroy()

    invoice_report_screen.protocol("WM_DELETE_WINDOW", get_invoices_by_period_on_close)


def save_invoice_record(selectedInvoiceID):
    global invoices_window
    global paidoutstanding_entry
    newPaidOutstanding = paidoutstanding_entry.get().strip()
    if newPaidOutstanding == "Paid":
        is_approved = True
    elif newPaidOutstanding == "Outstanding":
        is_approved = False
    else:
        Label(invoices_window, text="Error: Invalid input. Paid/Outstanding can only be Paid or Outstanding.", fg="red", font=("calibri", 11)).pack()
        paidoutstanding_entry.delete(0, END)

    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryInvoiceUpdate = "UPDATE Invoices SET InvoicePaid = ? WHERE InvoiceID = ?"
    
    cursor.execute(qryInvoiceUpdate, (is_approved, selectedInvoiceID)) 
    
    conn.commit()
    conn.close()
    Label(invoices_window, text="Record successfully updated.", fg="green", font=("calibri", 11)).pack()
    paidoutstanding_entry.delete(0, END)


def paidoutstanding(selectedInvoiceID):
    global invoiceinfo_window_window
    global invoices_window
    global main_screen
    global paidoutstanding_entry
    invoiceinfo_window_window.withdraw()
    invoices_window = Toplevel(main_screen)
    invoices_window.geometry("1280x720")
    invoices_window.title("Update Invoice Record")
    Label(invoices_window, text="Update Invoice Record", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(invoices_window, text="Please update the fields below. All fields marked with an asterisk (*) are mandatory. A guarantee can either be Paid or Outstanding.",).pack(pady=10)
    paidoutstanding = StringVar()
    #Paid/Outstanding
    paidoutstanding_label = Label(invoices_window, text="Paid/Outstanding *").pack()
    paidoutstanding_entry = Entry(invoices_window, textvariable=paidoutstanding)
    paidoutstanding_entry.pack()
    Button(invoices_window, text="Change Record", height="1", width="20", bg="blue", font=("Calibri", 13), command=lambda: save_invoice_record(selectedInvoiceID)).pack()
    def invoices_window_selected_on_close():
        invoiceinfo_window_window.deiconify()  # Show the main screen again
        invoices_window.destroy()

    invoices_window.protocol("WM_DELETE_WINDOW", invoices_window_selected_on_close)

def on_invoice_select(event):
    global invoicetree
    #Get the currently selected item IIDs
    selected_items = invoicetree.selection()
    if selected_items:
        #Get the first selected item's IID
        selected_item_iid = selected_items[0]
        # Retrieve all values associated with that specific row's IID
        item_details = invoicetree.item(selected_item_iid)
        # Extract just InvoiceID from the list of values
        selectedInvoiceID = item_details['values'][0] 
        # Call the next function with the StaffID
        paidoutstanding(selectedInvoiceID)

def GetInvoiceInfo():
    conn = sqlite3.connect("Backend.db")
    cursor = conn.cursor()
    qryInvoices = "SELECT * FROM Invoices"
    cursor.execute(qryInvoices)
    InvoiceResult = cursor.fetchall()
    return InvoiceResult

def EditInvoiceInfo():
    global main_staff_main_menu
    global main_screen
    global invoiceinfo_window_window
    global invoicetree
    main_staff_main_menu.withdraw()
    invoiceinfo_window_window = Toplevel(main_screen)
    invoiceinfo_window_window.geometry("1280x720")
    invoiceinfo_window_window.title("Edit Invoice Payment Information")
    Label(invoiceinfo_window_window, text="Edit Invoice Payment Information", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(invoiceinfo_window_window, text="Please choose a record below to update.",).pack(pady=10)
    style = ttk.Style()
    # Configure the Treeview to show vertical lines
    style.configure("Treeview", font=("Calibri", 14), rowheight=30, background="white", foreground="black", fieldbackground="white")
    # Add a border to each cell/heading
    style.configure("Treeview.Heading", background="lightgray", font=("Calibri", 15, "bold"))
    columns = ("InvoiceID", "CustomerID", "JobID", "QuoteID", "InvoicePrice", "InvoiceReason", "InvoiceExtraPrice", "InvoiceDate", "InvoicePaid")
    invoicetree = ttk.Treeview(invoiceinfo_window_window, columns=columns, show="headings")
    invoicetree.heading("InvoiceID", text="InvoiceID")
    invoicetree.heading("CustomerID", text="CustomerID")
    invoicetree.heading("JobID", text="JobID")
    invoicetree.heading("QuoteID", text="QuoteID")
    invoicetree.heading("InvoicePrice", text="InvoicePrice")
    invoicetree.heading("InvoiceReason", text="InvoiceReason")
    invoicetree.heading("InvoiceExtraPrice", text="InvoiceExtraPrice")
    invoicetree.heading("InvoiceDate", text="InvoiceDate")
    invoicetree.heading("InvoicePaid", text="InvoicePaid")
    invoicetree.column("InvoiceID", width=25)
    invoicetree.column("CustomerID", width=25)
    invoicetree.column("JobID", width=25)
    invoicetree.column("QuoteID", width=25)
    invoicetree.column("InvoicePrice", width=80)
    invoicetree.column("InvoiceReason", width=400)
    invoicetree.column("InvoiceExtraPrice", width=80)
    invoicetree.column("InvoiceDate", width=150)
    invoicetree.column("InvoicePaid", width=25)
    invoiceinfo = GetInvoiceInfo()
    for record in invoiceinfo:
        invoicetree.insert("", tk.END, values=record)
    invoicetree.pack(pady=20, fill=tk.BOTH, expand=True)
    invoicetree.bind("<<TreeviewSelect>>", on_invoice_select)
    Button(invoiceinfo_window_window, text="Return to Main Menu", height="1", width="20", bg="blue", font=("Calibri", 13), command=invoiceinfo_window_on_close).pack()

def invoiceinfo_window_on_close():
    main_staff_main_menu.deiconify() # Bring back the main menu
    invoiceinfo_window_window.destroy()

def create_work_history_pdf(records):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Previous Work History", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    # Records List Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "JOB RECORDS LIST:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    for record in records:
        
        job_id = record[0]
        customer_id = record[1]
        description = record[2]
        date_time = record[3]

        pdf.cell(0, 7, f"Job ID: {job_id} | Customer ID: {customer_id}", ln=True)
        
        pdf.multi_cell(0, 7, f"Description: {description}")
        pdf.cell(0, 7, f"Date/Time: {date_time}", ln=True)
        
        
        pdf.ln(5) 
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) 
        pdf.ln(5)

    filename = "PreviousWorkHistory.pdf"
    pdf.output(filename)
    return filename



def previouswork():
    global main_screen
    global main_staff_main_menu
    global previous_work_window
    main_staff_main_menu.withdraw()
    previous_work_window = Toplevel(main_screen)
    previous_work_window.geometry("1280x720")
    previous_work_window.title("Previous Work History (previouswork())")
    
    Label(previous_work_window, text="Previous Work History", bg="blue", 
          width="300", height="2", font=("Calibri", 13)).pack()
    
    Label(previous_work_window, text="Processing records and generating PDF...", font=("Calibri", 11)).pack()
    
    jobRecords = GetJobInfo()

    if jobRecords:
        pdf_filename = create_work_history_pdf(jobRecords)
        messagebox.showinfo("Success", f"PDF report generated: {pdf_filename}")
        os.startfile(pdf_filename) 
    else:
        messagebox.showwarning("No Data", "No job records found in the database.")
        label.config(text="No records found.")
    def previous_work_window_on_close():
        main_staff_main_menu.deiconify() # Bring back the main menu
        previous_work_window.destroy()

    previous_work_window.protocol("WM_DELETE_WINDOW", previous_work_window_on_close)
    
def mainstaffmainmenu():
    global main_staff_main_menu
    global main_screen
    global login_screen
    login_screen.withdraw()
    main_staff_main_menu = Toplevel(main_screen)
    main_staff_main_menu.geometry("1280x720")
    main_staff_main_menu.title("Main Staff Main Menu")
    Label(main_staff_main_menu, text="Main Staff Main Menu", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(main_staff_main_menu, text="Please click on the relevant option you would like to use in the program.",).pack(pady=10)
    Button(main_staff_main_menu, text="Update/Edit/Delete Customer Information", width=30, height=1, command=EditCustomerInformation).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Create Other Staff Accounts", width=30, height=1, command=createstaffaccount).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Delete Staff Accounts", width=30, height=1, command=DeleteStaffInformation).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Total Invoices by Day, Week and Month", width=30, height=1, command=total_invoices_by_period).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Previous Work History", width=30, height=1, command=previouswork).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Edit Invoice Payment Information", width=30, height=1, command=EditInvoiceInfo).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Access Staff Main Menu", width=30, height=1, command=staffmainmenu).pack()
    Label(main_staff_main_menu, text="").pack()
    Button(main_staff_main_menu, text="Logout", width=30, height=1, command=logout).pack()
    
def login_verify():
    global username_verify
    global password_login_entry
    global username_login_entry
    global password_verify
    global login_screen
    global role
    global CustomerID
    username_login_info = username_login_entry.get().strip()
    password_login_info = password_login_entry.get().strip()
    if (len(username_login_info)==0) or (len(password_login_info)==0):
        Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
        username_login_entry.delete(0, END)
        password_login_entry.delete(0, END)
    elif (len(username_login_info)<5) or (len(password_login_info)<8):
        Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
        username_login_entry.delete(0, END)
        password_login_entry.delete(0, END)
    else:
        hashed_password = hash_password(password_login_info)
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        qryCustomerLogin = "SELECT CustomerPassword FROM Customers WHERE CustomerUsername = ?"
        qryStaffLogin = "SELECT StaffPassword FROM Staff WHERE StaffUsername = ?"
        qryMainStaffLogin = "SELECT MainStaffPassword FROM MainStaff WHERE MainStaffUsername = ?"
        cursor.execute(qryCustomerLogin, (username_login_info,))
        customerresult_tuple = cursor.fetchone()

        cursor.execute(qryStaffLogin, (username_login_info,))
        staffresult_tuple = cursor.fetchone() 

        cursor.execute(qryMainStaffLogin, (username_login_info,))
        mainstaffresult_tuple = cursor.fetchone() 
        if customerresult_tuple:
            stored_hash = customerresult_tuple[0].strip() # Strip stored hash
            if hashed_password == stored_hash: # Compare stripped values
                # This code block is expected to run
                role = "Customer"
                qryCustomerID = "SELECT CustomerID FROM Customers WHERE CustomerUsername = ?"
                cursor.execute(qryCustomerID, (username_login_info,))
                CustomerIDTuple = cursor.fetchone()
                CustomerID = CustomerIDTuple[0]
                customermainmenu()
            else:
                # This is the block that is currently running
                Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
                username_login_entry.delete(0, END)
                password_login_entry.delete(0, END)
        # Apply the same logic to staff and mainstaff blocks
        elif staffresult_tuple:
            stored_hash = staffresult_tuple[0].strip() # Strip stored hash
            if hashed_password == stored_hash: # Compare stripped values
                role = "Staff"
                staffmainmenu()
            else:
                Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
                username_login_entry.delete(0, END)
                password_login_entry.delete(0, END)
        elif mainstaffresult_tuple:
            stored_hash = mainstaffresult_tuple[0].strip() # Strip stored hash
            if hashed_password == stored_hash: # Compare stripped values
                role = "Main Staff"
                mainstaffmainmenu()
            else:
                Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
                username_login_entry.delete(0, END)
                password_login_entry.delete(0, END)
        else:
            Label(login_screen, text="Error: Invalid username or password.", fg="red", font=("calibri", 11)).pack()
            username_login_entry.delete(0, END)
            password_login_entry.delete(0, END)
            
            
        
    
    
def login():
    global login_screen
    global main_screen
    main_screen.withdraw()
    login_screen = Toplevel(main_screen)
    login_screen.geometry("1280x720")
    login_screen.title("Login User (frmLogin)")
    Label(login_screen, text="Login User", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(login_screen, text="Please enter information into the fields below to log-in. "
    "All fields marked with an asterisk (*) are mandatory to fill in.",).pack(pady=10)
    global username_verify
    global password_verify
    global username_login_entry
    global password_login_entry
    username_verify = StringVar()
    password_verify = StringVar()
    Label(login_screen, text="Username *").pack()
    username_login_entry = Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack()
    Label(login_screen, text="").pack()
    Label(login_screen, text="Password *").pack()
    password_login_entry = Entry(login_screen, textvariable=password_verify, show="*")
    password_login_entry.pack()
    Label(login_screen, text="").pack()
    Button(login_screen, text="Login", width=10, height=1, command=login_verify).pack()
    photo = PhotoImage(file="watersafe-topspec_edited.gif")
    image = Label(login_screen, image=photo)
    image.pack()
    image.image = photo
    def login_on_close():
        main_screen.deiconify()  # Show the main screen again
        login_screen.destroy()

    login_screen.protocol("WM_DELETE_WINDOW", login_on_close)
    

    
def register_user():
    global username
    global password
    global username_entry
    global password_entry
    global firstname_entry
    global lastname_entry
    global emailaddress_entry
    global phonenumber_entry
    global houseaddress_entry
    global postcode_entry
    global register_screen
    global firstname
    global lastname
    global emailaddress
    global phonenumber
    global houseaddress
    global postcode
    global register_screen
    # gets all fields
    username_info = username_entry.get()
    password_info = password_entry.get()
    firstname_info = firstname_entry.get()
    lastname_info = lastname_entry.get()
    emailaddress_info = emailaddress_entry.get()
    phonenumber_info = phonenumber_entry.get()
    houseaddress_info = houseaddress_entry.get()
    postcode_info = postcode_entry.get()
    if (len(username_info) == 0) or (len(password_info) == 0):
        Label(register_screen, text="Error: Username and password must not be empty.", fg="red", font=("calibri", 11)).pack()
        username_entry.delete(0, END)
        password_entry.delete(0, END)
    elif (len(username_info) < 5) or (len(username_info) > 40):
        Label(register_screen, text="Error: Username must be between 5 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
        username_entry.delete(0, END)
    elif (len(password_info) < 8) or (len(password_info) > 40):
        Label(register_screen, text="Error: Password must be between 8 and 40 characters long.", fg="red", font=("calibri", 11)).pack()
        password_entry.delete(0, END)
    elif (len(firstname_info) == 0) or (len(firstname_info) > 50):
        Label(register_screen, text="Error: First Name must be between 1 and 50 characters long.", fg="red",font=("calibri", 11)).pack()
        firstname_entry.delete(0, END)
    elif (len(emailaddress_info) == 0) or (len(emailaddress_info) > 100):
        Label(register_screen, text="Error: Email Address must be between 1 and 100 characters long.", fg="red",font=("calibri", 11)).pack()
        emailaddress_entry.delete(0, END)
    elif ("@" not in emailaddress_info) or ("." not in emailaddress_info):
        Label(register_screen, text="Error: Invalid email format.", fg="red", font=("calibri", 11)).pack()
        emailaddress_entry.delete(0, END)
    elif (len(phonenumber_info) > 0) and (not phonenumber_info.isdigit()):
        Label(register_screen, text="Error: Phone Number must be numerical.", fg="red", font=("calibri", 11)).pack()
        phonenumber_entry.delete(0, END)
    elif (len(houseaddress_info) == 0) or (len(houseaddress_info) > 100):
        Label(register_screen, text="Error: House Address must be between 1 and 100 characters.", fg="red", font=("calibri", 11)).pack()
        houseaddress_entry.delete(0, END)
    elif (len(postcode_info) == 0) or (len(postcode_info) > 20):
        Label(register_screen, text="Error: Postcode must be between 1 and 20 characters.", fg="red", font=("calibri", 11)).pack()
        postcode_entry.delete(0, END)
    else:
        conn = sqlite3.connect("Backend.db")
        cursor = conn.cursor()
        password1 = hash_password(password_info)
        insertData = "INSERT INTO Customers(CustomerUsername, CustomerPassword, CustomerFirstName, CustomerSurname, CustomerEmailAddress, CustomerPhoneNumber, CustomerHouseAddress, CustomerPostcode) VALUES (?,?,?,?,?,?,?,?)"
        query = "SELECT * FROM Customers WHERE CustomerUsername = ?"
        cursor.execute(query, (username_info,))
        result = cursor.fetchone()
        if result:
            Label(register_screen, text="Error: Username already exists.", fg="red", font=("calibri", 11)).pack()
            username_entry.delete(0, END)
        else:
            cursor.execute(insertData, (username_info, password1, firstname_info, lastname_info, emailaddress_info, phonenumber_info, houseaddress_info, postcode_info))
            
            conn.commit()
            conn.close()
            Label(register_screen, text="Record Saved.",fg="green",font=("calibri, 11")).pack()
            username_entry.delete(0, END)
            password_entry.delete(0, END)
            firstname_entry.delete(0, END)
            lastname_entry.delete(0, END)
            emailaddress_entry.delete(0, END)
            phonenumber_entry.delete(0, END)
            houseaddress_entry.delete(0, END)
            postcode_entry.delete(0, END)
        
        
    
    
def register():
    global main_screen
    global register_screen
    global username, password, firstname, lastname, emailaddress, phonenumber, houseaddress, postcode, username_entry, password_entry, firstname_entry, lastname_entry, emailaddress_entry, phonenumber_entry, houseaddress_entry, postcode_entry
    main_screen.withdraw()

    register_screen = Toplevel(main_screen)
    register_screen.title("Register User (frmRegister)")
    
    register_screen.geometry("1280x720")

    # Connect to database
    #conn = sqlite3.connect("Backend.db")
    #cursor = conn.cursor()

    # Get next available CustomerID
    #cursor.execute("SELECT MAX(CustomerID) FROM Customers")
    #next_id = cursor.fetchone()[0]
    #next_id = (result + 1) if result else 1  # Start at 1 if no customers yet
    #conn.close()

    # Tkinter variables
    username = StringVar()
    password = StringVar()
    firstname = StringVar()
    lastname = StringVar()
    emailaddress = StringVar()
    phonenumber = StringVar()
    houseaddress = StringVar()
    postcode = StringVar()

    # Instruction label
    Label(register_screen, text="Register User", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(register_screen, text="Please enter information into the fields below to register. "
    "All fields marked with an asterisk (*) are mandatory to fill in.",).pack(pady=10)

    # Display CustomerID (label + disabled entry)
    #customerID_label = Label(register_screen, text="CustomerID *").pack()  # PACK the label!
    #customerID_entry = Entry(register_screen, width=30, state="disabled",
          #disabledbackground="lightgrey", disabledforeground="black",
          #textvariable=StringVar(value=str(next_id))).pack(pady=5)

    #Username
    username_label = Label(register_screen, text="Username *").pack()
    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack()
    #Password
    password_label = Label(register_screen, text="Password *").pack()
    password_entry = Entry(register_screen, textvariable=password, show="*")
    password_entry.pack()
    #Firstname
    firstname_label = Label(register_screen, text="First Name *").pack()
    firstname_entry = Entry(register_screen, textvariable=firstname)
    firstname_entry.pack()
    #Lastname
    lastname_label = Label(register_screen, text="Last Name *").pack()
    lastname_entry = Entry(register_screen, textvariable=lastname)
    lastname_entry.pack()
    #Emailaddress
    emailaddress_label = Label(register_screen, text="Email Address *").pack()
    emailaddress_entry = Entry(register_screen, textvariable=emailaddress)
    emailaddress_entry.pack()
    #Phonenumber
    phonenumber_label = Label(register_screen, text="Phone Number ").pack()
    phonenumber_entry = Entry(register_screen, textvariable=phonenumber)
    phonenumber_entry.pack()
    #Houseaddress
    houseaddress_label = Label(register_screen, text="House Address *").pack()
    houseaddress_entry = Entry(register_screen, textvariable=houseaddress)
    houseaddress_entry.pack()
    #Postcode
    postcode_label = Label(register_screen, text="Postcode *").pack()
    postcode_entry = Entry(register_screen, textvariable=postcode)
    postcode_entry.pack()
    #create Register User button
    Button(register_screen, text="Register User", height="1", width="20", bg="blue", font=("Calibri", 13), command=register_user).pack()
    #add top-spec plumbing logo
    photo = PhotoImage(file="watersafe-topspec_edited.gif")
    image = Label(register_screen, image=photo)
    image.pack()
    image.image = photo
    def register_on_close():
        main_screen.deiconify()  # Show the main screen again
        register_screen.destroy()

    register_screen.protocol("WM_DELETE_WINDOW", register_on_close)
    
    

    
def mainmenu():
    global main_screen
    main_screen = Tk()
    main_screen.geometry("300x250") #sets the configuration
    main_screen.title("Mainmenu") #sets the title of the window
    #create form label
    Label(text="Choose Login or Register", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(text="").pack()
    #create register button
    Button(text="Login", height="2", width="30", command=login).pack()
    Button(text="Register", height="2", width="30", command=register).pack()
    Label(text="").pack()
    photo = PhotoImage(file="watersafe-topspec_edited.gif")
    image = Label(main_screen, image=photo)
    image.pack()
    image.image = photo


mainmenu()
main_screen.mainloop()

