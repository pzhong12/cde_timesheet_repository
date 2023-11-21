import io
import time
import decimal
import json
from wtforms import SelectField
from flask import Flask, render_template, url_for, flash, redirect, send_file, request, session, make_response, jsonify
from forms import UserForm, LoginForm, TimesheetTable, UserFormTable, \
    TestForm, ProjectForm, ProjectFormTable, ClientFormTable, ClientForm, \
    DisciplineFormTable, DisciplineForm, ActivityFormTable, ActivityForm, UploadTimeSheet, TimesheetSummaryTable, ForgotPasswordForm, ResetPasswordForm, ApprovalCalendarForm
import sqlite3
import datetime
import calendar
import pandas
from form_functions import remove_from_database, check_existing, load_form, load_form_list, save_form, get_database_table, download_data, get_list, save_table, \
    delete_row, upload_excel, fill_form_list, get_project_list, convert_to_capital_letter, load_dynamic_form_list, load_dynamic_form, get_column_list, save_show_list, color_coding, color_coding_approval,\
    get_database_headers_info, download_multi_data, upload_multi_excel, get_dropdown_list, get_database_headers, find_username_by_email, update_password, update_download_log, find_email_by_username, get_access_privilege, get_query_data, generate_user_filling_timesheet_report
import traceback
import secrets
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from werkzeug.utils import secure_filename
import os
from io import BytesIO
from openpyxl import load_workbook

db_file = "data_base.db"
app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'd88a76722f415faa1fa9d24ce8175279'
print(app.secret_key)
serializer = URLSafeTimedSerializer(app.secret_key)
app.permanent_session_lifetime = datetime.timedelta(hours=12)

'''mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'timesheetcde@gmail.com'
app.config['MAIL_PASSWORD'] = 'Cde@2023!'''

def find_common_elements(array1, array2):
    if array1 == 'all':
        return array2
    if array2 == 'all':
        return array1
    set1 = set(array1)
    set2 = set(array2)
    common_elements = list(set1.intersection(set2))
    return common_elements

def send_email(email, subject, text_body):
    try:
        sender_email = 'timesheetcde@gmail.com'
        receiver_email = email
        sender_password = 'bbbuigxyvivhebqp'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        message = text_body
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except:
        traceback.print_exc()

def get_rejection_messages(form):
    users = []
    dates = []
    statuses = []

    for n in range(0, len(form.table_form), 1):

        for field in form.table_form[n]:
            fieldname_temp = ''.join((field.name).split('-')[2:])
            if fieldname_temp == 'user_name':
                users.append(field.data)
            if fieldname_temp == 'submit_date':
                dates.append(field.data)
            if fieldname_temp == 'status':
                statuses.append(field.data)
    print(f'users = {users}')
    print(f'dates = {dates}')
    print(f'status = {statuses}')

    selected_users = []
    selected_dates = []

    for n in range(0, len(users), 1):
        if statuses[n] == 'rejected':
            if users[n] not in selected_users:
                selected_users.append(users[n])
                selected_dates.append([dates[n]])
            else:
                user_index = selected_users.index(users[n])
                if dates[n] not in selected_dates[user_index]:
                    selected_dates[user_index].append(dates[n])

    receiver_emails = find_email_by_username(selected_users)

    return selected_users, selected_dates, receiver_emails


def generate_token(user_id):
    return serializer.dumps(user_id)

def verify_token(token, max_age=3600):  # Token expires in 1 hour
    try:
        user_id = serializer.loads(token, max_age=max_age)
        return user_id
    except:
        return None

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.submit.data:
        email = form.email.data
        try:
            user_name = find_username_by_email(email)
        except:
            flash('The email entered is invalid')
            return render_template('forgot_password.html')

        token = generate_token(user_name)
        #msg = Message(subject='CDE Timesheet Password Reset Request', recipients=[email])
        #msg.body = f'To reset your password, click on the following link: {url_for("reset_password", token=token, _external=True)}'


        sender_email = 'timesheetcde@gmail.com'
        receiver_email = email
        sender_password = 'bbbuigxyvivhebqp'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'cde timesheet password request'
        message = f'To reset your password, click on the following link: {url_for("reset_password", token=token, _external=True)}'
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        flash(f'Reset link sent to your email', 'success')
    return render_template('forgot_password.html', form=form)

# Create a route for password reset
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')

    if not token:
        flash('Invalid token.', 'error')
        return redirect(url_for('forgot_password'))

    user_id = verify_token(token)

    print(f'user id = {user_id}')
    if user_id is None:
        flash('Invalid or expired token. Please request a new password reset.', 'danger')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        new_password = form.password.data
        print(f'new password = {new_password}')
        update_password(user_id, new_password)
        flash('Password successfully reset. You can now log in with your new password.', 'success')
        return redirect(url_for('login'))  # Redirect to the login page

    return render_template('reset_password.html', form=form, user_name = user_id)

@app.route('/excel_spreadsheet', methods=['GET', 'POST'])
def excel_spreadsheet():
    print('calling excel server')
    print(request.form)
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)

    table_name_array = ['time_sheet', 'user', 'client', 'project', 'discipline', 'activity']

    header_info_array = get_database_headers_info(table_name_array)
    header_arrays = []
    for n in range(0, len(table_name_array), 1):
        header_arrays.append([])
        for m in range(0, len(header_info_array[n]), 1):
            if header_info_array[n][m][1] not in ['entry']:
                header_arrays[-1].append(header_info_array[n][m][1])

    checkbox_dict = {}
    for n in range(0, len(table_name_array), 1):
        temp_dict = {}
        for m in range(0, len(header_arrays[n]), 1):
            checkbox_value = request.form.get(table_name_array[n] + '--' + header_arrays[n][m], 'off')
            temp_dict[header_arrays[n][m]] = checkbox_value
        checkbox_dict[table_name_array[n]] = temp_dict
    print(checkbox_dict)

    table_names = [table_name for table_name in checkbox_dict.keys()]
    checked_headers = []
    for n in range(0, len(table_names), 1):
        checked_headers.append([])
        checkboxes = checkbox_dict[table_names[n]]
        keys = checkboxes.keys()
        for key in keys:
            if checkboxes[key] == 'on':
                checked_headers[-1].append(key)

    ###############overriding checkboxes#####################
    table_names = [table_name for table_name in table_name_array]
    checked_headers = []
    for table_name in table_names:
        checked_headers.append([])
        database_headers = get_database_headers(table_name)
        for header in database_headers:
            if header not in ['csrf_token', 'entry']:
                checked_headers[-1].append(header)
    #######################################################

    conditions = []
    for n in range(0, len(table_names), 1):
        conditions.append([])
        if table_names[n] == 'time_sheet':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            print(f'end_date: {end_date}')
            if start_date not in ['', None]:
                conditions[-1].append(['submit_date', '>=', start_date])
            if end_date not in ['', None]:
                conditions[-1].append(['submit_date', '<=', end_date])

    if 'download' in request.form:

        table_names = table_names + ['dropdown_list_setting'] + ['datatype_setting']
        print(f'table_names = {table_names}')
        checked_headers = checked_headers + [['target', 'source', 'criteria_1', 'filter_1', 'criteria_2', 'filter_2', 'criteria_3', 'filter_3', 'criteria_4', 'filter_4', 'dropdown_list_type']] + [['column_reference', 'datatype', 'uniqueness', 'special_type']]
        conditions = conditions + [[]] + [[]]

        response = download_multi_data(table_names, checked_headers, conditions)

        update_download_log('downloaded')
        return response


    if 'upload' in request.form:
        print('uploading')

        if 'file' not in request.files:
            return 'No file uploaded', 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return 'No file selected', 400

        # Process the uploaded file
        # You can save it to a specific location, perform further operations, etc.
        error_messages = upload_multi_excel(file)
        if len(error_messages) > 0:
            flash('Error uploading with following errors:', 'danger')
            for error_message in error_messages:
                flash(error_message, 'danger')
        else:
            update_download_log('uploaded')
            flash('Database updated!', 'success')

    if 'userFillingTimeSheetEndDate' in request.form:
        print('user_filling_timesheet')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date == '' or end_date == '':
            flash('Please enter start and end dates', 'danger')
            return render_template('excel_spreadsheet.html', table_name_array=table_name_array, header_arrays=header_arrays, user=user, access_list=access_list)
        print(f'start_date = {start_date}, end_date = {end_date}')
        response = generate_user_filling_timesheet_report(start_date, end_date)
        return response

    return render_template('excel_spreadsheet.html', table_name_array=table_name_array, header_arrays=header_arrays, user=user, access_list=access_list)


@app.route('/time_sheet_menu', methods=['GET', 'POST'])
def time_sheet_menu():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    return render_template('time_sheet_menu.html', user=user, access_list=access_list)


@app.route('/time_sheet_summary', methods=['GET', 'POST'])
def time_sheet_summary():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    print(f'user = {user}')
    display_headers = ['user_name', 'first_name', 'last_name', 'hours']

    Year = request.args.get('year')
    Month = request.args.get('month')
    Day = request.args.get('day')
    submit_date = datetime.datetime(year=int(Year), month=int(Month), day=int(Day))

    form_list = TimesheetSummaryTable()
    for field in form_list.table_form.entries:

        if field.select.data:
            #return redirect(url_for('time_sheet?username=' + field.user_name.data))
            print(f'directing to username = {field.user_name.data}')
            return redirect(url_for(f'time_sheet', year=Year, month=Month, day=Day, user_name=field.user_name.data, approval=True))

    table_name = 'time_sheet'
    conditions = [['submit_date', '=', submit_date], ['status', '!=', 'saved']]
    load_form_list(form_list, conditions, table_name)

    names = []
    hours = []
    '''for field in form_list.table_form.entries:
        print(f'username = {field.user_name.data}, hours = {field.hours.data}, comment = {field.comment.data},status = {field.status.data}')'''

    n = 0
    while n < len(form_list.table_form.entries):
        if form_list.table_form.entries[n].user_name.data not in names:
            names.append(form_list.table_form.entries[n].user_name.data)
            hours.append(float(form_list.table_form.entries[n].hours.data))
            n += 1
        else:
            index = names.index(form_list.table_form.entries[n].user_name.data)
            if form_list.table_form.entries[n].hours.data != None:
                hours[index] = hours[index] + float(form_list.table_form.entries[n].hours.data)

            form_list.table_form.entries.remove(form_list.table_form.entries[n])

    n = 0
    for field in form_list.table_form.entries:
        field.hours.data = hours[n]
        n += 1

    fill_form_list(form_list, 'user_name', 'user')

    return render_template('time_sheet_summary.html', form_list=form_list, headers=display_headers, user=user, access_list=access_list)

@app.route('/upload_time_sheet', methods=['GET', 'POST'])
def upload_time_sheet():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    form = UploadTimeSheet()

    if form.validate_on_submit():

        file = form.file.data

        table_name = 'time_sheet'
        index_headers = ['entry']
        check_tables = [None, None, 'user', 'client', 'project', 'discipline', 'activity', ['approved', 'rejected', 'submitted', 'saved']]
        check_headers = ['submit_date', 'hours', 'user_name', 'client', 'project', 'discipline', 'activity', 'status']
        error_messages = upload_excel(table_name, index_headers, file, check_headers=check_headers, check_tables=check_tables)

        if len(error_messages) > 0:
            for error_message in error_messages:
                flash(error_message, 'danger')
            return render_template('upload_time_sheet.html', form=form)
        else:
            flash('file successfully uploaded', 'success')
    else:
        print(form.errors)

    return render_template('upload_time_sheet.html', form=form, access_list=access_list)

@app.route('/activity_summary', methods=['GET', 'POST'])
def activity_summary():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    #headers = ['user_name', 'first_name', 'last_name', 'email', 'activity']
    form_list = ActivityFormTable()
    for field in form_list.table_form.entries:

        if field.edit.data:
            entry = field.entry.data

            return redirect(url_for('activity_form', entry=entry))

    table_name = 'activity'

    if form_list.download.data:

        conditions = []
        response = download_data(table_name, conditions)
        return response

    if form_list.upload.data:
        index_headers = ['activity']
        file = form_list.file.data

        upload_excel(table_name, index_headers, file)
        flash('File uploaded', 'success')
    if form_list.add.data:
        return redirect(url_for('activity_form'))

    load_condition = []
    headers = load_dynamic_form_list(form_list, load_condition, table_name)

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')
    print(f'headers = {headers}')
    print(f'user = {user}')
    print(f'show list = {show_list}')
    return render_template('activity_summary.html', form_list=form_list, headers=headers, user=user, show_list=show_list, access_list=access_list)

@app.route('/activity_form', methods=['GET', 'POST'])
def activity_form():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'activity'
    entry = request.args.get('entry')

    print(f'entry = {entry}')
    form = ActivityForm()
    load_condition = [['entry', '=', entry]]

    if entry not in [None, '']:
        status = 'edit'
    else:
        status = 'new'

    print(f'discipline before = {form.discipline.data}')
    headers = load_dynamic_form(form, load_condition, table_name, form_status=status)

    print(f'satus = {status}')

    remove_condition = [['entry', '=', entry]]

    if form.submit.data:
        print('submitting')
        activity = form.activity_name.data
        if status == 'new':
            print('new')
            print(f'activity = {activity}')
            ######## skip uniqueness #######
            #remove_condition = [['activity', '=', activity_name]]

            save_form(form, remove_condition, table_name)
            flash(f'New activity {form.activity.data} created!', 'success')
            return redirect(url_for('activity_summary'))
            ##################
            '''activity_exists = check_existing(table_name, remove_condition)
            if activity_exists:
                flash('The activity ' + activity + ' already exist', 'danger')
            else:
                save_form(form, remove_condition, table_name)
                flash(f'New activity {form.activity.data} created!', 'success')
                return redirect(url_for('activity_summary'))'''
        else:
            print('updating')
            load_condition = [['entry', '=', entry]]
            ##### testing ########
            print(f'discipline = {form.discipline.data}')
            #######################
            save_form(form, load_condition, table_name)
            flash(f' Activity {activity} updated!', 'success')
            return redirect(url_for('activity_summary'))

    if form.delete.data:
        if entry != None:
            print('deleting form')
            remove_from_database(remove_condition, table_name)
            return redirect(url_for('activity_summary'))
        else:
            print('deleting new activity form')
            return redirect(url_for('activity_summary'))

    return render_template('activity_form.html', form=form, status=status, user=user, headers=headers, access_list=access_list)

@app.route('/discipline_summary', methods=['GET', 'POST'])
def discipline_summary():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)

    #headers = ['user_name', 'first_name', 'last_name', 'email', 'discipline']
    form_list = DisciplineFormTable()
    for field in form_list.table_form.entries:

        if field.edit.data:
            entry = field.entry.data

            return redirect(url_for('discipline_form', entry=entry))

    table_name = 'discipline'

    if form_list.download.data:

        conditions = []
        response = download_data(table_name, conditions)
        return response

    if form_list.upload.data:
        index_headers = ['discipline_name']
        file = form_list.file.data

        upload_excel(table_name, index_headers, file)
        flash('File uploaded', 'success')
    if form_list.add.data:
        return redirect(url_for('discipline_form'))

    load_condition = []
    headers = load_dynamic_form_list(form_list, load_condition, table_name)

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')
    print(f'headers = {headers}')
    print(f'user = {user}')
    print(f'show list = {show_list}')
    return render_template('discipline_summary.html', form_list=form_list, headers=headers, user=user, show_list=show_list, access_list=access_list)

@app.route('/discipline_form', methods=['GET', 'POST'])
def discipline_form():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'discipline'
    entry = request.args.get('entry')

    print(f'entry = {entry}')
    form = DisciplineForm()
    load_condition = [['entry', '=', entry]]


    if entry not in [None, '']:
        status = 'edit'
    else:
        status = 'new'

    headers = load_dynamic_form(form, load_condition, table_name, form_status=status)

    print(f'satus = {status}')

    remove_condition = [['entry', '=', entry]]

    if form.submit.data:
        print('submitting')
        discipline = form.discipline.data
        if status == 'new':
            print('new')
            print(f'discipline = {discipline}')
            remove_condition = [['discipline', '=', discipline]]
            discipline_exists = check_existing(table_name, remove_condition)
            if discipline_exists:
                flash('The discipline ' + discipline + ' already exist', 'danger')
            else:
                save_form(form, remove_condition, table_name)
                flash(f'New discipline {form.discipline.data} created!', 'success')
                return redirect(url_for('discipline_summary'))
        else:
            print('updating')
            load_condition = [['entry', '=', entry]]
            save_form(form, load_condition, table_name)
            flash(f' Discipline {discipline} updated!', 'success')
            return redirect(url_for('discipline_summary'))

    if form.delete.data:
        if entry != None:
            print('deleting form')
            remove_from_database(remove_condition, table_name)
            return redirect(url_for('discipline_summary'))
        else:
            return redirect(url_for('discipline_summary'))

    return render_template('discipline_form.html', form=form, status=status, user=user, headers=headers, access_list=access_list)

@app.route('/client_summary', methods=['GET', 'POST'])
def client_summary():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    #headers = ['user_name', 'first_name', 'last_name', 'email', 'discipline']
    form_list = ClientFormTable()
    for field in form_list.table_form.entries:

        if field.edit.data:
            entry = field.entry.data

            return redirect(url_for('client_form', entry=entry))

    table_name = 'client'

    if form_list.download.data:

        conditions = []
        response = download_data(table_name, conditions)
        return response

    if form_list.upload.data:
        index_headers = ['client']
        file = form_list.file.data

        upload_excel(table_name, index_headers, file)
        flash('File uploaded', 'success')
    if form_list.add.data:
        return redirect(url_for('client_form'))

    load_condition = []
    headers = load_dynamic_form_list(form_list, load_condition, table_name)

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')
    print(f'headers = {headers}')
    print(f'user = {user}')
    print(f'show list = {show_list}')
    return render_template('client_summary.html', form_list=form_list, headers=headers, user=user, show_list=show_list, access_list=access_list)

@app.route('/client_form', methods=['GET', 'POST'])
def client_form():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'client'
    entry = request.args.get('entry')

    print(f'entry = {entry}')
    form = ClientForm()
    load_condition = [['entry', '=', entry]]


    if entry not in [None, '']:
        status = 'edit'
    else:
        status = 'new'

    headers = load_dynamic_form(form, load_condition, table_name, form_status=status)

    print(f'satus = {status}')

    remove_condition = [['entry', '=', entry]]

    if form.submit.data:
        print('submitting')
        client = form.client.data
        if status == 'new':
            print('new')
            print(f'client = {client}')
            remove_condition = [['client', '=', client]]
            client_exists = check_existing(table_name, remove_condition)
            if client_exists:
                flash('The client ' + client + ' already exist', 'danger')
            else:
                save_form(form, remove_condition, table_name)
                flash(f'New client {form.client.data} created!', 'success')
                return redirect(url_for('client_summary'))
        else:
            print('updating')
            load_condition = [['entry', '=', entry]]
            save_form(form, load_condition, table_name)
            flash(f' Client {client} updated!', 'success')
            return redirect(url_for('client_summary'))

    if form.delete.data:
        if entry != None:
            print('deleting form')
            remove_from_database(remove_condition, table_name)
            return redirect(url_for('client_summary'))
        else:
            return redirect(url_for('client_summary'))

    return render_template('client_form.html', form=form, status=status, user=user, headers=headers, access_list=access_list)

@app.route('/tester', methods=['GET', 'POST'])
def tester():

    form = TestForm()
    if form.Submit.data:
        print(form.MultiOptions.data)

    return render_template('tester.html', form=form)

@app.route('/setting')
def setting():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    return render_template('setting.html', user=user, access_list=access_list)

@app.route('/project_summary', methods=['GET', 'POST'])
def project_summary():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
    #headers = ['user_name', 'first_name', 'last_name', 'email', 'discipline']

    form_list = ProjectFormTable()

    for field in form_list.table_form.entries:

        if field.edit.data:
            entry = field.entry.data

            return redirect(url_for('project_form', entry=entry))

    table_name = 'project'

    if form_list.download.data:

        conditions = []
        response = download_data(table_name, conditions)
        return response

    if form_list.upload.data:
        index_headers = ['project']
        file = form_list.file.data

        upload_excel(table_name, index_headers, file)
        flash('File uploaded', 'success')
    if form_list.add.data:
        return redirect(url_for('project_form'))

    load_condition = []

    headers = load_dynamic_form_list(form_list, load_condition, table_name)

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')
    print(f'project summary')

    return render_template('project_summary.html', form_list=form_list, headers=headers, user=user, show_list=show_list, access_list=access_list)

@app.route('/project_form', methods=['GET', 'POST'])
def project_form():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'project'
    entry = request.args.get('entry')

    print(f'entry = {entry}')
    form = ProjectForm()

    load_condition = [['entry', '=', entry]]


    if entry not in [None, '']:
        status = 'edit'
    else:
        status = 'new'

    headers = load_dynamic_form(form, load_condition, table_name, form_status=status)

    print(f'satus = {status}')

    remove_condition = [['entry', '=', entry]]

    if form.submit.data:
        print('submitting')
        project = form.project.data
        if status == 'new':
            print('new')
            print(f'project = {project}')
            remove_condition = [['project', '=', project]]
            project_exists = check_existing(table_name, remove_condition)
            if project_exists:
                flash('The project ' + project + ' already exist', 'danger')
            else:
                save_form(form, remove_condition, table_name)
                flash(f'New project {form.project.data} created!', 'success')
                return redirect(url_for('project_summary'))
        else:
            print('updating')
            load_condition = [['entry', '=', entry]]
            save_form(form, load_condition, table_name)
            flash(f' Project {project} updated!', 'success')
            return redirect(url_for('project_summary'))

    if form.delete.data:
        if entry != None:
            print('deleting form')
            remove_from_database(remove_condition, table_name)
            return redirect(url_for('project_summary'))
        else:
            return redirect(url_for('project_summary'))

    return render_template('project_form.html', form=form, status=status, user=user, headers=headers, access_list=access_list)

@app.route('/user_summary', methods=['GET', 'POST'])
def user_summary():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    #headers = ['user_name', 'first_name', 'last_name', 'email', 'discipline']
    form_list = UserFormTable()
    for field in form_list.table_form.entries:

        if field.edit.data:
            entry = field.entry.data
            print('calling user form from summary')
            return redirect(url_for('user_form', entry=entry))

    table_name = 'user'

    if form_list.download.data:

        conditions = []
        response = download_data(table_name, conditions)
        return response

    if form_list.upload.data:
        index_headers = ['user_name']
        file = form_list.file.data

        upload_excel(table_name, index_headers, file)
        flash('File uploaded', 'success')
    if form_list.add.data:
        return redirect(url_for('user_form'))

    load_condition = []
    headers = load_dynamic_form_list(form_list, load_condition, table_name)

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')
    print(f'headers = {headers}')
    print(f'user = {user}')
    print(f'show list = {show_list}')
    return render_template('user_summary.html', form_list=form_list, headers=headers, user=user, show_list=show_list, access_list=access_list)

@app.route('/user_form', methods=['GET', 'POST'])
def user_form():
    print('user form called')
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'user'
    entry = request.args.get('entry')

    print(f'entry = {entry}')
    form = UserForm()
    load_condition = [['entry', '=', entry]]

    if entry not in [None, '']:
        status = 'edit'
    else:
        status = 'new'

    headers = load_dynamic_form(form, load_condition, table_name, form_status=status)
    print(f'header list from dynamic form = {headers}')
    print(f'satus = {status}')

    remove_condition = [['entry', '=', entry]]

    if form.submit.data:
        print('submitting')
        user_name = form.user_name.data
        if status == 'new':
            print('new')
            print(f'user_name = {user_name}')
            remove_condition = [['user_name', '=', user_name]]
            user_exists = check_existing(table_name, remove_condition)
            if user_exists:
                flash('The user ' + user_name + ' already exist', 'danger')
            else:
                save_form(form, remove_condition, table_name)
                flash(f'New user {form.user_name.data} created!', 'success')
                return redirect(url_for('user_summary'))
        else:
            print('updating')
            load_condition = [['entry', '=', entry]]
            save_form(form, load_condition, table_name)
            flash(f' user {user_name} updated!', 'success')
            return redirect(url_for('user_summary'))

    if form.delete.data:
        if entry != None:
            print('deleting form')
            remove_from_database(remove_condition, table_name)
            return redirect(url_for('user_summary'))
        else:
            return redirect(url_for('user_summary'))
    return render_template('user_form.html', form=form, status=status, user=user, headers=headers, access_list=access_list)

@app.route('/')
def homepage():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)

    return render_template('home.html', user=user, access_list=access_list)

@app.route('/download_time_sheet', methods=['GET', 'POST'])
def download_time_sheet():
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)

    start_date = None
    end_date = None
    selected_list = []
    option_list = []
    user_data = []
    selected_headers = ['client', 'project', 'discipline', 'activity', 'user']
    hours_header = 'hours'
    hours = []

    ######################### get table from date range ###################################
    try:
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        conditions = [['submit_date', '>=', start_date], ['submit_date', '<=', end_date]]
        user_data, hours = get_database_table('time_sheet', conditions, selected_headers, hours_header)
    except:
        traceback.print_exc()
        pass
    #################################################################################################

    if selected_list == None or selected_list == []:
        if len(user_data) > 0:
            selected_list = [[] for _ in range(len(user_data[0]))]

    if option_list == None or option_list == []:

        transposed_user_data = list(zip(*user_data))
        option_list = []
        for n in range(0, len(transposed_user_data), 1):
            option_list.append(['Select All', 'Deselect All'])
            for m in range(0, len(transposed_user_data[n]), 1):
                value = transposed_user_data[n][m]
                if not value in option_list[n]:
                    option_list[n].append(value)

    if 'downloadTimeSheet' in request.form:
        ####### get selected list #########
        option_strings = request.form.getlist('option')

        selected_list = []
        for option_string in option_strings:
            option_string_no_prefix = option_string[2:]
            if option_string[0] == 'Y':
                selected_list.append([])
            if option_string[1] == 'y':
                selected_list[-1].append(option_string_no_prefix)

        option_list = []
        for option_string in option_strings:
            option_string_no_prefix = option_string[2:]
            if option_string[0] == 'Y':
                option_list.append([])
            option_list[-1].append(option_string_no_prefix)

        conditions = []

        if start_date != None and start_date != '':
            conditions.append(['submit_date', '>=', start_date])

        if end_date != None and end_date != '':
            conditions.append(['submit_date', '<=', end_date])

        for n in range(0, len(selected_list), 1):
            selected = selected_list[n]
            #selected = ["'" + item + "'" for item in selected]
            header = selected_headers[n]
            if len(selected) > 0:
                #conditions.append(header.lower() + ' in (' + ', '.join(selected) + ')')
                conditions.append([header.lower(), 'in', selected])

        response = download_data('time_sheet', conditions)

        return response

    return render_template('download_time_sheet.html', startDate=start_date, endDate=end_date, optionList=option_list, selectedList=selected_list, userData=user_data, headers=selected_headers, hours=hours, user=user, access_list=access_list)# hours_index=hours_index)

@app.route('/approval_calendar', methods=['GET', 'POST'])
def approval_calendar():
    user = ''
    access_list = []
    if 'user_name' in session:
        print('hello ' + session['user_name'])
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)

    form = ApprovalCalendarForm()

    if form.approval.data:
        date_array = form.selected_date.data.split(',')[1:]
        print(f'date array from approval = {date_array}')
        date_array_json = json.dumps(date_array)
        return redirect(url_for('approval', date_array=date_array_json))

    month_to_num = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    Year = request.args.get('year')
    Month = request.args.get('month')
    if type(Year) == str:
        Year = int(Year)
    if type(Month) == str:
        Month = int(Month)

    if Year == None and Month == None:
        Year = datetime.datetime.now().year
        Month = datetime.datetime.now().month

    days = []
    colors = []
    total_hours = []
    accumulated_approved_hours = 0
    statuses = []

    first_day = 1
    last_day = calendar.monthrange(Year, Month)[1]
    first_weekday = datetime.datetime(year=Year, month=Month, day=first_day).weekday()
    last_weekday = datetime.datetime(year=Year, month=Month, day=last_day).weekday()

    leading_days = first_weekday + 1
    if leading_days == 7:
        leading_days = 0
    trailing_days = 5 - last_weekday
    if trailing_days == -1:
        trailing_days = 6

    first_date = datetime.datetime(year=Year, month=Month, day=first_day) - datetime.timedelta(days=leading_days)
    last_date = datetime.datetime(year=Year, month=Month, day=last_day) + datetime.timedelta(days=trailing_days)

    number_of_rows = round((last_date - first_date + datetime.timedelta(days=1)) / datetime.timedelta(days=7))

    Date = first_date

    for m in range(0, number_of_rows, 1):

        colors.append([])
        days.append([])
        total_hours.append([])
        statuses.append([])

        for n in range(0, 7, 1):
            days[m].append(Date.day)

            if Date.month == Month:
                color, hours, approved_hours, status = color_coding_approval(Date)
                colors[m].append(color)
                total_hours[m].append(hours)
                statuses[m].append(status)
                if approved_hours not in [0, '', None]:
                    accumulated_approved_hours += approved_hours
            else:
                colors[m].append("grey")
                total_hours[m].append('')
                statuses[m].append('')
            Date = Date + datetime.timedelta(days=1)

        month_text = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August', '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        year_month = month_text[str(Month)] + ' ' + str(Year)

    return render_template('approval_calendar.html', year=Year, month=Month, year_month=year_month, days=days, colors=colors, user=user, total_hours=total_hours, accumulated_approved_hours=accumulated_approved_hours, statuses=statuses, form=form, access_list=access_list)

@app.route('/calendar')
def calendar_month():
    user = ''
    access_list = []
    if 'user_name' in session:

        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    month_to_num = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
               'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    Year = request.args.get('year')
    Month = request.args.get('month')
    if type(Year) == str:
        Year = int(Year)
    if type(Month) == str:
        Month = int(Month)


    if Year == None and Month == None:
        Year = datetime.datetime.now().year
        Month = datetime.datetime.now().month

    days = []
    colors = []
    total_hours = []
    statuses = []
    accumulated_approved_hours = 0

    first_day = 1
    last_day = calendar.monthrange(Year, Month)[1]
    first_weekday = datetime.datetime(year=Year, month=Month, day=first_day).weekday()
    last_weekday = datetime.datetime(year=Year, month=Month, day=last_day).weekday()

    leading_days = first_weekday + 1
    if leading_days == 7:
        leading_days = 0
    trailing_days = 5 - last_weekday
    if trailing_days == -1:
        trailing_days = 6

    first_date = datetime.datetime(year=Year, month=Month, day=first_day) - datetime.timedelta(days=leading_days)
    last_date = datetime.datetime(year=Year, month=Month, day=last_day) + datetime.timedelta(days=trailing_days)

    number_of_rows = round((last_date - first_date + datetime.timedelta(days=1)) / datetime.timedelta(days=7))

    Date = first_date

    for m in range(0, number_of_rows, 1):

        colors.append([])
        days.append([])
        total_hours.append([])
        statuses.append([])

        for n in range(0, 7, 1):
            days[m].append(Date.day)

            if Date.month == Month:
                #colors[m].append("white")
                color, hours, approved_hours, status = color_coding(Date, user)
                colors[m].append(color)
                total_hours[m].append(hours)
                statuses[m].append(status)
                if approved_hours not in [0, '', None]:
                    accumulated_approved_hours += approved_hours
            else:
                colors[m].append("grey")
                total_hours[m].append('')
                statuses[m].append('')
            print(f'statuses = {statuses}')
            print(f'total hours = {total_hours}')
            Date = Date + datetime.timedelta(days=1)


        month_text = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August', '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        year_month = month_text[str(Month)] + ' ' + str(Year)
    print(colors)
    print(total_hours)

    return render_template('calendar.html', year=Year, month=Month, year_month=year_month, days=days, colors=colors, user=user, total_hours=total_hours, accumulated_approved_hours=accumulated_approved_hours, statuses=statuses, access_list=access_list)

@app.route('/logout')
def logout():
    if 'user_name' in session:
        session.clear()
        flash('Log out successful', 'success')
    return redirect(url_for('homepage', user=''))

@app.route('/download/<file>')
def download_file(file):
    #relative path based on folder where this .py is saved'
    filename = file
    return send_file(filename, as_attachment=True)

@app.route('/upload/<file_type>', methods=['POST'])
def upload_file(file_type):
    print(file_type)
    file = request.files['file']
    # do something on the file
    return redirect(url_for('homepage'))

@app.route('/time_sheet',  methods=['GET', 'POST'])
def time_sheet():

    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'time_sheet'
    #headers = ['entry', 'user_name', 'submit_date', 'client', 'project', 'discipline', 'activity', 'hours', 'comment', 'status']
    time_sheet_year = int(request.args.get('year'))
    time_sheet_month = int(request.args.get('month'))
    time_sheet_day = int(request.args.get('day'))
    time_sheet_date = datetime.datetime(year=time_sheet_year, month=time_sheet_month, day=time_sheet_day)
    approval = request.args.get('approval')
    print(f'approval = {approval}')
    user_name = request.args.get('user_name')

    if user_name == None:
        user_name = user

    form = TimesheetTable()


    if len(form.table_form.entries) > 0 and not form.copy_from_date.data:
        options_list = json.loads(form.options_list.data)
        for row in form.table_form.entries:
            entry_number = row.entry.data
            print(f'entry number = {entry_number}')
            for field in row:
                fieldname_with_entry = ''.join((field.name + '_' + str(entry_number)).split('-')[2:])
                if fieldname_with_entry in options_list:
                    field.choices = options_list[fieldname_with_entry]['choices']
                    field.data = options_list[fieldname_with_entry]['selected']

    if form.copy_from_date.data:
        load_conditions = [['user_name', '=', user_name], ['submit_date', '=', datetime.datetime.strptime(str(form.copy_date_selection.data), "%Y-%m-%d")]]
        while len(form.table_form.entries) > 0:
            form.table_form.pop_entry()

        headers = load_dynamic_form_list(form, load_conditions, table_name)
        for n in range(0, len(form.table_form), 1):
            for field in form.table_form[n]:

                field_name = ''.join((field.name).split('-')[2:])

                print(f'field name from time sheet = {field_name}')
                if field_name == 'entry':
                    field.data = ''
                elif field_name == 'submit_date':
                    field.data = time_sheet_date
                elif field_name == 'status':
                    field.data = ''

    else:
        if user == 'admin' and user_name != 'admin':
            load_conditions = [['user_name', '=', user_name], ['submit_date', '=', time_sheet_date], ['status', '!=', 'saved']]
        else:
            load_conditions = [['user_name', '=', user_name], ['submit_date', '=', time_sheet_date]]

        print(f'load condition = {load_conditions}')
        if len(form.table_form.entries) == 0:
            headers = load_dynamic_form_list(form, load_conditions, table_name)
        else:
            _, headers = get_column_list(table_name)

    if form.add_field.data:

        form.table_form.append_entry()
        row_headers = []
        row_values = []
        form.table_form[-1].user_name.data = user_name
        for field in form.table_form[-1]:
            fieldname_temp = ''.join((field.name).split('-')[2:])
            row_headers.append(fieldname_temp)
            if fieldname_temp == 'user_name':
                row_values.append([user_name])
            else:
                row_values.append([''])
            if fieldname_temp == 'status':
                if field.data in [None, 'None', 'none']:
                    field.data = ''

        for field in form.table_form[-1]:
            if type(field) == SelectField:
                dropdown_list = get_dropdown_list(table_name, ''.join((field.name).split('-')[2:]), None, headers=row_headers, cell_values=row_values)
                print('adding a row')
                print(f'fieldname = {field.name}')
                print(f'headers = {headers}')
                print(f'cell values = {row_values}')
                print(f'dropdown list = {dropdown_list}')
                field.choices = dropdown_list
                field.value = ''


    remove_conditions = []
    for field in form.table_form.entries:
        if field.remove.data:
            #load_data = False
            form.table_form.entries.remove(field)

    if form.approve.data:
        #load_data = False
        for field in form.table_form.entries:
            field.status.data = 'approved'

    if form.reject.data:
        #load_data = False
        for field in form.table_form.entries:
            field.status.data = 'rejected'

    if form.save.data or form.submit.data:
        print('saving')
        if len(form.table_form.entries) > 0:
            print(form.table_form[-1])
            print(form.table_form[-1].client)
        table_to_be_saved = []
        headers_to_be_saved = []

        for row in form.table_form.entries:
            row_to_be_saved = []
            for field in row:
                splitname = field.name.split('-')
                if len(splitname) >= 3:
                    fieldname = '-'.join(splitname[2:])
                else:
                    fieldname = field.name
                if fieldname == 'submit_date':
                    field.data = time_sheet_date
                elif fieldname == 'status':

                    if form.save.data:
                        if approval:
                            if field.data not in ['approved', 'submitted', 'rejected']:
                                field.data = 'saved'
                        else:
                            if field.data not in ['approved', 'submitted']:
                                field.data = 'saved'
                    if form.submit.data:
                        print('submitted data')
                        print(f'status = {field.data}')
                        if field.data != 'approved':
                            field.data = 'submitted'

                    if form.save.data:
                        pass
                        #if field.data not in ['approved', 'submitted']:
                        #    field.data = 'saved'
                    if form.submit.data:
                        print('submitted data')
                        print(f'status = {field.data}')
                        if field.data != 'approved':
                            field.data = 'submitted'

                if type(field.data) == decimal.Decimal:
                    field.data = float(field.data)
                print(f'saving field: {field.name} = {field.data}')

                if fieldname != 'remove':
                    row_to_be_saved.append(field.data)

                if fieldname not in headers_to_be_saved and fieldname != 'remove':
                    headers_to_be_saved.append(fieldname)
            table_to_be_saved.append(tuple(row_to_be_saved))
        print(f'headers to be saved = \n {headers_to_be_saved}')
        print(f'table to be saved = \n {table_to_be_saved}')

        save_conditions = []

        entry_index = headers_to_be_saved.index('entry')
        for n in range(0, len(table_to_be_saved), 1):
            save_conditions.append([['entry', '=', table_to_be_saved[n][entry_index]]])

        save_table(table_name, save_conditions, table_to_be_saved, headers_to_be_saved)

        removed_list = form.removed_list.data.split(',')[0:-1]

        for removed_row in removed_list:
            remove_conditions.append([['entry', '=', int(removed_row)]])

        for remove_condition in remove_conditions:
            remove_from_database(remove_condition, table_name)

        form = TimesheetTable()
        while len(form.table_form.entries) > 0:
            form.table_form.pop_entry()
        headers = load_dynamic_form_list(form, load_conditions, table_name)

    if form.save_to_template.data:
        print('saving template')
        table_to_be_saved = []
        headers_to_be_saved = []
        for row in form.table_form.entries:
            row_to_be_saved = []
            for field in row:
                splitname = field.name.split('-')
                if len(splitname) >= 3:
                    fieldname = '-'.join(splitname[2:])
                else:
                    fieldname = field.name
                #if fieldname == 'submit_date':
                #    field.data = ''
                #elif fieldname == 'status':
                #    field.data = ''
                #elif fieldname == 'user_name':
                #    field.data = field.data + '$template'

                if type(field.data) == decimal.Decimal:
                    field.data = float(field.data)
                print(f'saving field: {field.name} = {field.data}')

                if fieldname != 'remove':
                    row_to_be_saved.append(field.data)

                if fieldname not in headers_to_be_saved and fieldname != 'remove':
                    headers_to_be_saved.append(fieldname)
            status_index = headers_to_be_saved.index('status')
            submit_date_index = headers_to_be_saved.index('submit_date')
            #username_index = headers_to_be_saved.index('user_name')
            row_to_be_saved[status_index] = 'template'
            row_to_be_saved[submit_date_index] = ''
            #row_to_be_saved[username_index] = row_to_be_saved[username_index] + '$template'
            table_to_be_saved.append(tuple(row_to_be_saved))

        save_conditions = []

        for n in range(0, len(table_to_be_saved), 1):
            save_conditions.append([])
        remove_condition = [['user_name', '=', user_name], ['status', '==', 'template']]
        remove_from_database(remove_condition, table_name)
        save_table(table_name, save_conditions, table_to_be_saved, headers_to_be_saved)

    if form.restore_from_template.data:
        #load_conditions = [['user_name', '=', user_name + '$template']]
        load_conditions = [['user_name', '=', user_name], ['status', '==', 'template']]
        while len(form.table_form.entries) > 0:
            form.table_form.pop_entry()
        headers = load_dynamic_form_list(form, load_conditions, table_name)
        for row in form.table_form.entries:
            for field in row:
                splitname = field.name.split('-')
                if len(splitname) >= 3:
                    fieldname = '-'.join(splitname[2:])
                else:
                    fieldname = field.name
                if fieldname == 'status':
                    field.data = ''
                if fieldname == 'submit_date':
                    field.data = time_sheet_date

    for formfield in form.table_form.entries:
        formfield.user_name.data = user_name
        fill_form_list(form, 'user_name', 'user')

    first_name = ''
    last_name = ''

    if len(form.table_form.entries) > 0:
        first_name = form.table_form.entries[0].first_name.data
        last_name = form.table_form.entries[0].last_name.data

    show_list, _ = get_column_list(table_name)
    if 'password' in headers:
        headers.remove('password')

    approval_status = None
    if not approval:
        _, _, _, approval_status = color_coding(time_sheet_date, user_name=user_name)

    if approval == 'true' and user != 'admin':
        flash('user needs to be admin to approve time sheet', 'danger')
        return redirect(url_for('homepage'))

    return render_template('time_sheet.html', form=form, first_name=first_name, last_name=last_name, user=user, user_name=user_name, year=time_sheet_year, month=time_sheet_month, day=time_sheet_day, headers=headers, show_list=show_list, approval=approval, approval_status=approval_status, access_list=access_list)

@app.route('/approval', methods=['GET', 'POST'])
def approval():
    print('approval called')
    user = ''
    access_list = []
    if 'user_name' in session:
        user = session['user_name']
        if user not in ['', None]:
            access_list = get_access_privilege(user)
    table_name = 'time_sheet'

    form = TimesheetTable()

    if len(form.table_form.entries) > 0:
        options_list = json.loads(form.options_list.data)
        for row in form.table_form.entries:
            entry_number = row.entry.data
            for field in row:
                fieldname_with_entry = ''.join((field.name + '_' + str(entry_number)).split('-')[2:])
                if fieldname_with_entry in options_list:
                    field.choices = options_list[fieldname_with_entry]['choices']
                    field.data = options_list[fieldname_with_entry]['selected']

    date_array = []
    if len(form.table_form.entries) == 0:
        date_array_json = request.args.get('date_array')
        date_string_array = json.loads(date_array_json)
        print(f'date_array = {date_string_array}')
        date_array = []
        for date_string in date_string_array:
            date_array.append(datetime.datetime.strptime(date_string, "%Y-%m-%d"))

    load_conditions = []
    for n in range(0, len(date_array), 1):
        load_condition = ['submit_date', '=', date_array[n]]
        load_conditions.append(load_condition)

    and_or = None
    for n in range(0, len(date_array) - 1, 1):
        and_or = 'or'

    print(f'load condition = {load_conditions}')
    if len(form.table_form.entries) == 0:
        headers = load_dynamic_form_list(form, load_conditions, table_name, and_or=and_or)
    else:
        _, headers = get_column_list(table_name)

    print(f'number of rows = {len(form.table_form.entries)}')

    show_list, _ = get_column_list(table_name)
    print(f'show list = {show_list}')

    if form.add_field.data:

        form.table_form.append_entry()
        ############### add a value to added row ##################
        sortDict = json.loads(form.sort_status.data)
        print(f'sortDict = {sortDict}')
        if 'summaryId' in sortDict.keys():
            splitText = sortDict['summaryId'].split('-')
            if len(splitText) > 0:
                headerText = splitText[0]
                headerValue = '-'.join(splitText[1:]).replace('_colon_', ':').replace('_semicolon_', ';').replace('_space_',
                                                                                                               ' ')
                print(f'header text = {headerText}')
                print(f'header text = {headerValue}')
            else:
                headerText = None
                headerValue = None

            for field in form.table_form[-1]:
                fieldname_temp = ''.join((field.name).split('-')[2:])
                if fieldname_temp == headerText:
                    field.data = headerValue
        ####################################################
        row_headers = []
        row_values = []

        for field in form.table_form[-1]:
            fieldname_temp = ''.join((field.name).split('-')[2:])
            row_headers.append(fieldname_temp)
            if fieldname_temp == 'user_name':
                row_values.append([''])
            else:
                row_values.append([''])
            if fieldname_temp == 'status':
                if field.data in [None, 'None', 'none']:
                    field.data = ''

        for field in form.table_form[-1]:
            if type(field) == SelectField:
                dropdown_list = get_dropdown_list(table_name, ''.join((field.name).split('-')[2:]), None, headers=row_headers, cell_values=row_values)
                print('adding a row')
                print(f'fieldname = {field.name}')
                print(f'headers = {headers}')
                print(f'cell values = {row_values}')
                print(f'dropdown list = {dropdown_list}')
                field.choices = dropdown_list
                field.value = ''

    remove_conditions = []
    for field in form.table_form.entries:
        if field.remove.data:
            # load_data = False
            form.table_form.entries.remove(field)

    if form.approve.data:
        # load_data = False
        for field in form.table_form.entries:
            field.status.data = 'approved'

    if form.reject.data:
        # load_data = False
        for field in form.table_form.entries:
            field.status.data = 'rejected'

    if form.save.data:
        print('saving')
        if len(form.table_form.entries) > 0:
            print(form.table_form[-1])
            print(form.table_form[-1].client)
        table_to_be_saved = []
        headers_to_be_saved = []
        selected_users, dates_rejected, receiver_emails = get_rejection_messages(form)
        for n in range(0, len(selected_users), 1):
            subject = 'CDE timesheet rejection'
            message = 'The following dates for timesheet submission has been rejected: \n'
            for m in range(0, len(dates_rejected[n]), 1):
                message = message + f'{dates_rejected[n][m]}\n'
            send_email(receiver_emails[n], subject, message)

        for row in form.table_form.entries:
            row_to_be_saved = []
            for field in row:
                splitname = field.name.split('-')
                if len(splitname) >= 3:
                    fieldname = '-'.join(splitname[2:])
                else:
                    fieldname = field.name

                if type(field.data) == decimal.Decimal:
                    field.data = float(field.data)
                print(f'saving field: {field.name} = {field.data}')

                if fieldname != 'remove':
                    row_to_be_saved.append(field.data)

                if fieldname not in headers_to_be_saved and fieldname != 'remove':
                    headers_to_be_saved.append(fieldname)
            table_to_be_saved.append(tuple(row_to_be_saved))
        print(f'headers to be saved = \n {headers_to_be_saved}')
        print(f'table to be saved = \n {table_to_be_saved}')

        save_conditions = []

        entry_index = headers_to_be_saved.index('entry')
        for n in range(0, len(table_to_be_saved), 1):
            save_conditions.append([['entry', '=', table_to_be_saved[n][entry_index]]])

        save_table(table_name, save_conditions, table_to_be_saved, headers_to_be_saved)

        removed_list = form.removed_list.data.split(',')[0:-1]

        for removed_row in removed_list:
            remove_conditions.append([['entry', '=', int(removed_row)]])

        for remove_condition in remove_conditions:
            remove_from_database(remove_condition, table_name)

        form = TimesheetTable()
        while len(form.table_form.entries) > 0:
            form.table_form.pop_entry()

        date_array_json = request.args.get('date_array')
        date_string_array = json.loads(date_array_json)
        print(f'date_array 2nd = {date_string_array}')
        date_array = []
        for date_string in date_string_array:
            print(f'date string = {date_string}')
            date_array.append(datetime.datetime.strptime(date_string, "%Y-%m-%d"))
        load_conditions = []
        for n in range(0, len(date_array), 1):
            load_condition = ['submit_date', '=', date_array[n]]
            load_conditions.append(load_condition)
        print(f'load conditions 2nd = {load_conditions}')
        headers = load_dynamic_form_list(form, load_conditions, table_name, and_or='or')

    return render_template('approval.html', user=user, form=form, show_list=show_list, headers=headers, access_list=access_list)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = UserForm()
    first_name = form.first_name.data
    last_name = form.last_name.data
    user_name = form.user_name.data
    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        cursor.execute('SELECT EXISTS(SELECT 1 from user where user_name = ?)', (user_name,))
        user_name_exists = cursor.fetchone()[0]
        cursor.execute('SELECT EXISTS(SELECT 1 from user where email = ?)', (email,))
        email_exists = cursor.fetchone()[0]

        if user_name_exists:
            flash('The username ' + user_name + ' already exist', 'danger')
            cursor.close()
            connection.close()
        elif email_exists:
            flash('The email ' + user_name + ' already exist', 'danger')
            cursor.close()
            connection.close()
        else:
            row_data = (user_name, password, email, first_name, last_name)
            cursor.execute("insert into user values (?,?,?,?,?)", row_data)
            connection.commit()
            cursor.close()
            connection.close()
            flash(f'Account created for {form.user_name.data}!', 'success')
            return redirect(url_for('homepage'))

    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user_name = form.user_name.data
        password = form.password.data

        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT EXISTS(SELECT 1 from user where user_name = ?)', (user_name,))
        row_exists = cursor.fetchone()[0]
        if row_exists:
            cursor.execute("SELECT password FROM user where user_name = ?", (user_name,))
            password_fetched = cursor.fetchone()[0]
            if password_fetched == password:
                cursor.close()
                connection.close()
                session['user_name'] = user_name
                flash('You have been logged in as ' + session['user_name'], 'success')
                return redirect(url_for("homepage", user=user_name))
            else:
                flash('Login unsuccessful. Please check user_name and password', 'danger')
                cursor.close()
                connection.close()

    return render_template('login.html', title='Login', form=form, user='')

@app.route('/submit-form', methods=['POST'])
def submit_form():
    name = request.form['name']

    return redirect(url_for('homepage'))

@app.route('/generate_webform_dropdown_list', methods=['POST'])
def generate_webform_dropdown_list():
    print('request received')
    data = request.get_json()
    table_name = data.get('table_name')
    target_column = data.get('target_column')
    entry_index = None
    headers = data.get('headers')
    cell_values = data.get('cell_values')

    dropdown_list = get_dropdown_list(table_name, target_column, entry_index, headers=headers, cell_values=cell_values)
    print(f'table_name = {table_name}')
    print(f'target_column = {target_column}')
    print(f'headers = {headers}')
    print(f'cell_values = {cell_values}')
    print(f'dropdown_list = {dropdown_list}')
    response_data = {
        'message': 'AJAX request received successfully', 'dropdown_list': dropdown_list
    }

    return jsonify(response_data)

@app.route('/save_display_list', methods=['POST'])
def save_display_list():
    print('request received')
    data = request.get_json()
    show_list = data.get('show_list')
    table_name = data.get('table_name')
    print(f'show_list = {show_list}')
    print(f'table_name = {table_name}')
    save_show_list(table_name, show_list)
    response_data = {
        'message': 'AJAX request received successfully',
    }

    return jsonify(response_data)

@app.route('/user_filter', methods=['POST'])
def user_filter():
    print('user filter request received')
    data = request.get_json()
    table = data.get('table')
    column = data.get('column')
    raw_list = 'all'
    for n in range(0, len(table), 1):
        query = f'SELECT {column[n]} FROM {table[n]}'
        print(f'query for user filter = {query}')
        print(f'raw list1 = {raw_list}')
        print(f'raw list2 = {list(get_query_data(query))}')
        query_list = list(get_query_data(query))
        query_list_unpacked = []
        for tup_item in query_list:
            if tup_item[0] is not None:
                split_texts = tup_item[0].split(',')
                for split_text in split_texts:
                    if split_text.strip() not in query_list_unpacked:
                        query_list_unpacked.append(split_text.strip())

        raw_list = find_common_elements(raw_list, query_list_unpacked)
        print(raw_list)

    response_data = {
        'message': 'AJAX request received successfully', 'user_list': raw_list
    }

    return jsonify(response_data)

if __name__ == '__main__':
    #app.run()
    #app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=5001)
    #app.run(host='192.168.12.12')

