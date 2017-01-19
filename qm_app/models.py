from tracker import db, udb, lm
from flask_mongoengine.wtf import model_form
from datetime import datetime
from wtforms import DateField, Form, TextField,StringField,BooleanField, SelectMultipleField, validators
from flask_admin.form import widgets
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired
from flask_login import UserMixin

class User(UserMixin, udb.Model):
    __tablename__ = 'users'
    id = udb.Column(udb.Integer, primary_key=True)
    #social_id = udb.Column(udb.String(64), nullable=False, unique=True)
    nickname = udb.Column(udb.String(64), nullable=False)
    email = udb.Column(udb.String(64), nullable=True)
    picture = udb.Column(udb.String(64), nullable=True)
    
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


class SoftwareComponent(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return "%s - %s" % (self.code,self.description) 
    
class SoftwarePackage(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    components = db.ListField(db.ReferenceField(SoftwareComponent))
    def __str__(self):
        return self.code
    
class ReleaseStatus(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code

class DeviceVersion(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code
    
class Release(db.Document):
    package = db.ReferenceField(SoftwarePackage, required=True)
    creation_date = db.DateTimeField(required=True, default=datetime.now())
    major_version = db.IntField(required=True)
    minor_version = db.IntField()
    revision_version = db.IntField(required=True)
    repository = db.StringField(max_length=1024, required=True)
    status = db.ReferenceField(ReleaseStatus)
    release_notes = db.StringField(max_length=20000)
    requires_update_add = db.BooleanField(default=False)
    device_version = db.ReferenceField(DeviceVersion)
    meta = {'strict' : False}
    def url_id(self):
        return "%s/%d/%d/%d" % (self.package, self.major_version, self.minor_version if self.minor_version != None else 0, self.revision_version )

    def safe_url_id(self):
        return "%s_%d_%d_%d" % (self.package, self.major_version, self.minor_version if self.minor_version != None else 0, self.revision_version )
            
    def __str__(self):
        #print self.package, self.major_version, self.minor_version, self.revision_version 
        return "%s %d.%d.%d" % (self.package, self.major_version, self.minor_version if self.minor_version != None else 0, self.revision_version )
    
class Implementation(db.Document):
    date =  db.DateTimeField(default=datetime.now())
    affected_comopnents = db.ListField(db.ReferenceField(SoftwareComponent), required=True)
    repository = db.StringField(max_length=1024)

class SoftwareRequirement(db.Document):
    srs_id = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=1500, required=True)
    created = db.DateTimeField(default=datetime.now, required=True)
    def __str__(self):
        return self.srs_id
    
class IssueStatus(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code
    
class IssueType(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code

class Severity(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code

class Issue(db.Document):
    issue_id = db.SequenceField(value_decorator = lambda x: "issue-" + str(x))
    issue_type = db.ReferenceField(IssueType)
    description = db.StringField(max_length=1500)
    srs = db.ReferenceField(SoftwareRequirement)
    created = db.DateTimeField(default=datetime.now())
    affected_components = db.ListField(db.ReferenceField(SoftwareComponent))
    status = db.ReferenceField(IssueStatus)
    comments = db.ListField(db.StringField(max_length=250))
    #implemented_in = db.ReferenceField(Release, required=False)
    implemented_in_aux = db.ListField(db.ReferenceField(Release, required=False))
    def __str__(self):
        return self.issue_id


class TestType(db.Document):
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code

class TestStatus(db.Document):    
    code = db.StringField(max_length=15, required=True, unique=True)
    description = db.StringField(max_length=150)
    def __str__(self):
        return self.code
    
class TestStep(db.EmbeddedDocument):
    description = db.StringField(max_length=1500)
    expected_outcome = db.StringField(max_length=1500)
        
class Test(db.Document):
    test_id = db.SequenceField(value_decorator = lambda x: "test-" + str(x))
    test_type = db.ReferenceField(TestType)
    #issue = db.ReferenceField(Issue)
    issues = db.ListField(db.ReferenceField(Issue))
    components = db.ListField(db.ReferenceField(SoftwareComponent))
    tested_in = db.ListField(db.ReferenceField(Release))
    description = db.StringField(max_length=1500)
    status = db.ReferenceField(TestStatus)
    steps = db.ListField(db.EmbeddedDocumentField(TestStep))
    report_location=db.StringField(max_length=1024)
    attachments = db.ListField(db.FileField())
    def __str__(self):
        return self.test_id


class Risk(db.Document):
    risk_id = db.SequenceField(value_decorator = lambda x: "risk-" + str(x))
    parent_issue = db.ReferenceField(Issue)
    description = db.StringField(max_length=1500)
    mitigations = db.ListField(db.ReferenceField(Test))
    mitigation_description = db.StringField(max_length=1500)
    severity = db.ReferenceField(Severity)
    severity_after = db.ReferenceField(Severity)
    comments = db.ListField(db.StringField(max_length=250))

    def __str__(self):
        return self.risk_id

class SoftwareBundle(db.Document):
    id = db.SequenceField(value_decorator = lambda x: "sw-update-" + str(x))
    name = db.StringField(max_length=255)
    description = db.StringField(max_length=1500)
    date = db.DateTimeField(required=True, default=datetime.now())
    device_version = db.ReferenceField(DeviceVersion)
    releases = db.ListField(db.ReferenceField(Release))
    
SoftwareRequirementForm = model_form(SoftwareRequirement)
IssueForm = model_form(Issue)
IssueForm.created.format = "%Y-%m-%d"
ReleaseForm = model_form(Release)
RiskForm = model_form(Risk)
TestForm = model_form(Test)
TestForm.attachments = None
TestStepForm = model_form(TestStep)
TestStepForm.test_id = TextField(u'Test id')

BundleForm = model_form(SoftwareBundle)

class IssueSearchForm(Form):
    issue_id = TextField(u'Issue id', [validators.length(max=15)])
    description = TextField(u'Description', [validators.length(max=15)])
    created_after =  DateField('Created after' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    created_before =  DateField('Created before' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    updated_after =  DateField('Updated after' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    updated_before =  DateField('Updated before' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    status = SelectMultipleField("Status", choices=[], coerce=unicode)
    issue_type = SelectMultipleField("Type", choices=[], coerce=unicode)
    affected_components = SelectMultipleField("Components", choices=[], coerce=unicode)
    
    
class SrsSearchForm(Form):
    srs_id = TextField(u'Id', [validators.length(max=15)])
    description = TextField(u'Description', [validators.length(max=15)])
    created_after =  DateField('Created after' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    created_before =  DateField('Created before' , format = '%Y-%m-%d', widget=widgets.DatePickerWidget)
    ord = TextField(u'Order', [validators.length(max=15)], default="+srs_id")
    
class ReleaseSearchForm(Form):
    sw_package = SelectField(u"SW-package", choices=[]);# SoftwarePackage
    device_version = SelectField(u"Device version", choices=[]);

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    