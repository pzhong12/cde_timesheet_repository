from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FieldList, FormField, DecimalField, DateField, SelectMultipleField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from form_functions import get_list, get_project_list
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import Select
from markupsafe import Markup



def reformat_list(list1, list2):
    array = []
    for n in range(0, len(list1), 1):
        array.append((list1[n], list2[n]))

class ApprovalCalendarForm(FlaskForm):
    selected_date = StringField('Selected Date', name='selected_date')
    submit = SubmitField('submit', name='submit')
    approval = SubmitField('Approval')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email')
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=20)], name='password')
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], name='confirm_password')
    submit = SubmitField('Submit')

class UploadTimeSheet(FlaskForm):
    file = FileField('File', name='time_sheet_file', validators=[FileRequired()])
    submit = SubmitField('Upload', name='submit')

class ActivityForm(FlaskForm):
    #activity_name = StringField('Activity Name', validators=[DataRequired()], name='activity_name')
    #activity_description = StringField('Activity Description', validators=[DataRequired()], name='activity_description')
    submit = SubmitField('Save', name='save')
    delete = SubmitField('Delete', name='delete')
    edit = SubmitField('Edit', name='edit')
    entry = IntegerField('Entry', name='entry')

class ActivityFormTable(FlaskForm):
    table_form = FieldList(FormField(ActivityForm), min_entries=0)
    download = SubmitField('Download Activity Data')
    file = FileField('File', name='activity_file', validators=[FileRequired()])
    upload = SubmitField('Upload Activity Data')
    add = SubmitField('Add Activity')
    sort_status = StringField('Sort Status', name='sort_status')

class DisciplineForm(FlaskForm):
    #discipline_name = StringField('Discipline Name', validators=[DataRequired()], name='discipline_name')
    #discipline_description = StringField('Discipline Description', validators=[DataRequired()], name='discipline_description')
    submit = SubmitField('Save', name='save')
    delete = SubmitField('Delete', name='delete')
    edit = SubmitField('Edit', name='edit')
    entry = IntegerField('Entry', name='entry')

class DisciplineFormTable(FlaskForm):
    table_form = FieldList(FormField(DisciplineForm), min_entries=0)
    download = SubmitField('Download Discipline Data')
    file = FileField('File', name='discipline_file', validators=[FileRequired()])
    upload = SubmitField('Upload Discipline Data')
    add = SubmitField('Add Discipline')
    sort_status = StringField('Sort Status', name='sort_status')

class ClientForm(FlaskForm):
    #client_name = StringField('Client Name', validators=[DataRequired()], name='client_name')
    #contact_person = StringField('Contact Person', name='contact_person')
    #phone_number = StringField('Phone Number', name='phone_number')
    #address = StringField('Address', name='address')
    #postal_code = StringField('Postal Code', name='postal_code')
    submit = SubmitField('Save', name='save')
    delete = SubmitField('Delete', name='delete')
    edit = SubmitField('Edit', name='edit')
    #entry = IntegerField('Entry', name='entry')

class ClientFormTable(FlaskForm):
    table_form = FieldList(FormField(ClientForm), min_entries=0)
    download = SubmitField('Download Client Data')
    file = FileField('File', name='client_file', validators=[FileRequired()])
    upload = SubmitField('Upload Client Data')
    add = SubmitField('Add Client')
    sort_status = StringField('Sort Status', name='sort_status')

class ProjectForm(FlaskForm):
    client_list = get_list('client', 'client_name', ['client_name'], ' ')
    user_list = get_list('user', 'user_name', ['first_name', 'last_name'], ' ')
    #project_name = StringField('Project Name', validators=[DataRequired()], name='project_name')
    #project_lsd = StringField('LSD', validators=[DataRequired()], name='lsd')
    #project_owner = SelectField('Owner', choices=client_list, validators=[DataRequired()], name='owner')
    #project_manager = SelectMultipleField('Project Manager', choices=user_list, name='project_manager')
    #project_engineer = SelectMultipleField('Project Engineer', choices=user_list, name='project_engineer')
    #stress_engineer = SelectMultipleField('Stress Engineer', choices=user_list, name='stress_engineer')
    #civil_engineer = SelectMultipleField('Civil Engineer', choices=user_list, name='civil_engineer')
    #electrical_engineer = SelectMultipleField('Electrical Engineer', choices=user_list, name='electrical_engineer')
    #drafting_lead = SelectMultipleField('Drafting Lead', choices=user_list, name='drafting_lead')

    submit = SubmitField('Save')
    delete = SubmitField('Delete')
    edit = SubmitField('Edit')
    entry = IntegerField('Entry', name='entry')

class ProjectFormTable(FlaskForm):
    table_form = FieldList(FormField(ProjectForm), min_entries=0)
    download = SubmitField('Download Project Data')
    file = FileField('File', name='project_file', validators=[FileRequired()])
    upload = SubmitField('Upload Project Data')
    add = SubmitField('Add Project')
    sort_status = StringField('Sort Status', name='sort_status')

class UserForm(FlaskForm):
    discipline_list = get_list('discipline', 'discipline_name', ['discipline_description'], ' ')
    group_list = ['Drafting', 'Engineering', 'Electrical']
    #service_list = ['Project Engineer', 'Stress Engineer', 'Checker', 'Electrical Engineer', 'CSA Lead']
    #employment_type_list = ['Employee', 'Contractor']
    #user_name = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)], name='user_name')
    #first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)], name='first_name')
    #last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)], name='last_name')
    #phone_number = StringField('Phone Number', name='phone_number')
    #email = StringField('Email', validators=[DataRequired(), Email()], name='email')
    #discipline = SelectMultipleField('Discipline', choices=discipline_list, name='discipline')
    #group = SelectMultipleField('Group', choices=group_list, name='group')
    #service = SelectMultipleField('Service', choices=service_list, name='service')
    #employment_type = SelectField('Employment Type', choices=employment_type_list, name='employment_type')
    #date_of_hire = DateField('Hire Date', name='hire_date')
    #password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)], name='password')
    #confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], name='confirm_password')
    submit = SubmitField('Save', name='save')
    delete = SubmitField('Delete', name='delete')
    edit = SubmitField('Edit', name='edit')
    #entry = IntegerField('Entry', name='entry')

class UserFormTable(FlaskForm):
    table_form = FieldList(FormField(UserForm), min_entries=0)
    download = SubmitField('Download User Data')
    file = FileField('File', name='user_file', validators=[FileRequired()])
    upload = SubmitField('Upload User Data')
    add = SubmitField('Add User')
    sort_status = StringField('Sort Status', name='sort_status')

class LoginForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired()], name='user_name')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)], name='password')
    remember = BooleanField('Remember me', name='remember_me')
    submit = SubmitField('Login', name='login')
    entry = IntegerField('Entry', name='entry')

class TimesheetSummary(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired()], name='user_name')
    first_name = StringField('First Name', validators=[DataRequired()], name='first_name')
    last_name = StringField('Last Name', validators=[DataRequired()], name='last_name')
    hours = DecimalField('Hours', name='hours')
    select = SubmitField('Select', name='select')
    submit_date = DateField('submit_date', name='submit_date')


class TimesheetSummaryTable(FlaskForm):
    table_form = FieldList(FormField(TimesheetSummary), min_entries=0)
    sort_status = StringField('Sort Status', name='sort_status')
    #group_header = StringField('Group Header', name='group_header')

class TimesheetForm(FlaskForm):

    client_list = get_list('client', 'client_name', ['client_name'], '')
    project_list = get_list('project', 'project_name', ['project_name'], '')
    status_choices = [('', ''), ('approved', 'Approved'), ('rejected', 'Rejected'), ('saved', 'Saved'), ('submitted', 'Submitted')]
    activity_list = get_list('activity', 'activity_name', ['activity_description'], ' ')
    discipline_list = get_list('discipline', 'discipline_name', ['discipline_description'], ' ')
    #client = SelectField('Client', choices=client_list, validators=[DataRequired()], name='client_name')
    #project = SelectField('Project', choices=project_list, validators=[DataRequired()], name='project_name')
    #discipline = SelectField('Discipline', choices=discipline_list, validators=[DataRequired()], name='discipline_name')
    #activity = SelectField('Activity', choices=activity_list, validators=[DataRequired()], name='activity_name')
    #hours = DecimalField('Hours', validators=[DataRequired(), NumberRange(min=0.0, max=16.0, message='range')], name='hours')
    #status = SelectField('Status', choices=status_choices, name='status')
    #entry = IntegerField('Entry', name='entry')
    #comment = StringField('Comment', validators=[DataRequired()], name='comment')
    remove = SubmitField('Remove', render_kw={'class': 'remove_row'}, name='remove')
    #first_name = StringField('First Name', name='first_name')
    #last_name = StringField('Last Name', name='last_name')
    #user_name = StringField('username', name='user_name')

class TimesheetTable(FlaskForm):

    table_form = FieldList(FormField(TimesheetForm), min_entries=0)
    add_field = SubmitField('Add Field', render_kw={'class': 'add_row'}, name='add_field')
    submit = SubmitField('Submit', render_kw={'class': 'submit_table'}, name='submit')
    save = SubmitField('Save', name='save')
    approve = SubmitField('Approve All', name='approve')
    reject = SubmitField('Reject All', name='reject')
    removed_list = StringField('Removed List', name='removed_list')
    options_list = StringField('Options List', name='options_list')
    sort_status = StringField('Sort Status', name='sort_status')
    copy_date_selection = DateField('Copy date selection', name='copy_date_selection')
    copy_from_date = SubmitField('Copy from date', name='copy_from_date')
    save_to_template = SubmitField('Save to template', name='save_to_template')
    restore_from_template = SubmitField('Restore from template', name='restore_from_template')

class DownloadTimeSheet(FlaskForm):
    employee_list = get_list('user', 'user_name', ['first_name', 'last_name'], ' ')
    employee = SelectField('Client', choices=employee_list, validators=[DataRequired()], name='employee')
    start_date = DateField('Start date', format='%Y-%m-%d', validators=[DataRequired()], name='start_date')
    end_date = DateField('End date', format='%Y-%m-%d', validators=[DataRequired()], name='end_date')
    download_time_sheet = SubmitField('Download Time Sheet')

######## user setting #######
class UserSummaryForm(FlaskForm):
    user_name = StringField('Username', name='user_name')
    number = StringField('Phone Number', name='phone_number')
    first_and_last_name = StringField('Name', name='name')
    email = StringField('Email')
    discipline = StringField('Discipline', name='discipline')
    remove = SubmitField('Delete User', name='delete_user')
    edit = SubmitField('Edit User', name='edit_user')

class UserSummaryTable(FlaskForm):
    table_form = FieldList(FormField(UserSummaryForm), min_entries=0)
    add_field = SubmitField('Add Field', render_kw={'class': 'add_row'}, name='add_field')
    save = SubmitField('Save', name='save')

class TestForm(FlaskForm):
    MultiOptions = SelectMultipleField('multi_options', choices=[('', ''), ('1', 'Option 1'), ('2', 'Option 2')])
    Submit = SubmitField('submit')

