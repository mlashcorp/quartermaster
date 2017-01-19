from flask import request, abort, redirect, url_for, render_template, make_response, session, g, flash
from tracker import app, db, udb, csrf , lm
from tracker.models import *
from datetime import datetime
from werkzeug.utils import secure_filename
from gridfs import GridFS
from mongoengine.fields import GridFSProxy, get_db, ObjectId
from gridfs.errors import NoFile 
import sys, traceback
from flask_login import login_user, logout_user, current_user, login_required
from auth import *

ALLOWED_EXTENSIONS = set(['csv'])
ASSAY_FILE_DIR = "/home/biosurfit/code/assay-manager/aim/uploads/"
approved_admin_users = ['kikio77@gmail.com','mlashcorp@gmail.com','cortereal.biosurfit@gmail.com','josenogueira.biosurfit@gmail.com']

def register_user(username,email,picture):
    # Create the user. Try and use their name returned by Google,
    # but if it is not set, split the email address at the @.
    nickname = username
    if nickname is None or nickname == "":
        nickname = email.split('@')[0]

    # We can do more work here to ensure a unique nickname, if you 
    # require that.
    user=User(nickname=nickname, email=email, picture=picture)
    udb.session.add(user)
    udb.session.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/new_release")
#@login_required
def new_release():
    return render_template('new_release.html',form=ReleaseForm(),issue=IssueForm(),risk=RiskForm(),test=TestForm())

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    # Flask-Login function
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email, picture = oauth.callback()
    if email is None:
        # I need a valid email address for my user identification
        flash('Authentication failed.')
        logout_user()
        return redirect(url_for('index'))

    # Look if the user already exists
    user=User.query.filter_by(email=email).first()
    if not user and email in approved_admin_users:
        register_user(username,email,picture)
        user=User.query.filter_by(email=email).first()

    if not user:
        # I need a valid email address for my user identification
        flash('Authentication failed.')
        logout_user()
        return redirect(url_for('index'))
        
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    login_user(user, remember=False)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print "g.user is: "+str(g.user)
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html',
                           title='Sign In')

@app.before_request
def before_request():
    g.user = current_user


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    #for package in packages:
    #    release = Release.objects.get(package=package, major_version=major, minor_version=minor, revision_version=revision)
    
    #release_form = ReleaseForm(request.form)
    #find latest release from each software item
    search_form = ReleaseSearchForm(request.form)
    sw_packages = SoftwarePackage.objects
    releases = []
    for  package in sw_packages:
        objects= Release.objects(package=package).order_by('package', '-major_version',  '-minor_version', '-revision_version')
        releases.append(objects[0])
        #print objects[0].release_notes
    print u"g.user is: "+unicode(g.user.nickname)+" "+unicode(g.user.picture)
    return render_template('dashboard.html', releases=releases,username=g.user.nickname,picture=g.user.picture)

@app.route('/find_srs', methods=['GET','POST'])
def find_srs():

    search_form = SrsSearchForm(request.form)
    requirement_form = SoftwareRequirementForm()
    if request.method == 'POST':
        query_dict = {}
    
        if search_form.srs_id.data != None and len(search_form.srs_id.data) > 0:
            query_dict["srs_id__contains"] = search_form.srs_id.data
            
        if search_form.description.data != None and len(search_form.description.data) > 0: 
            query_dict["description__contains"] = search_form.description.data
#                                 #created__lte = search_form.created_before.data )
        print query_dict
        objects = SoftwareRequirement.objects(**query_dict)
    else:
        objects = SoftwareRequirement.objects
        
    return render_template('find_srs.html', search_form=search_form, requirement_form=requirement_form, srss=objects.order_by(search_form.ord.data))

@app.route('/srs_overview/<srs_id>', methods=['GET','POST'])
def srs_overview(srs_id):

    objects = SoftwareRequirement.objects(srs_id=srs_id)
    srs = None if len(objects) == 0 else objects[0]
    
    requirement_form = SoftwareRequirementForm(obj=srs)
    
    issues = Issue.objects(srs=srs)
    issue_form = IssueForm()
    issue_form.srs.data=srs
    
    return render_template('srs_overview.html', srs=srs, issues=issues , requirement_form=requirement_form, issue_form=issue_form)
 
@app.route('/add_srs', methods=['GET','POST'])
def add_srs():

    form = SoftwareRequirementForm(request.form)
    if request.method == 'POST':
        print "created date", form.created.data
        if form.validate():
            
            try:
                print request.form["id"]
                srs = SoftwareRequirement.objects.get(id= request.form["id"])
            except:
                srs = SoftwareRequirement()
            
            form.populate_obj(srs)
            srs.save()
            return redirect("srs_overview/" + srs.srs_id)
        else:                
            print "Invalid form " + str(form.errors)
    
    return render_template('add_srs.html', requirement_form=form)   

@app.route('/find_issues', methods=['GET','POST'])
def find_issues():
    
    search_form = IssueSearchForm(request.form)
    
    if request.method == 'POST':
        
        query_dict = {}
        
        if search_form.issue_id.data != None and len(search_form.issue_id.data) > 0:
            print search_form.issue_id.data 
            query_dict["issue_id__contains"] = search_form.issue_id.data
            
        if search_form.issue_type.data != None and len(search_form.issue_type.data) > 0: 
            print search_form.issue_type.data
            query_dict["issue_type__in"] = search_form.issue_type.data
            
        if search_form.status.data != None and len(search_form.status.data) > 0: 
            print search_form.status.data
            query_dict["status__in"] = search_form.status.data
            
        if search_form.affected_components.data != None and len(search_form.affected_components.data) > 0: 
            print search_form.affected_components.data
            query_dict["affected_components__in"] = search_form.affected_components.data
            
        if search_form.status.data != None and len(search_form.status.data) > 0: 
            print search_form.status.data
            query_dict["affected_components__in"] = search_form.affected_components.data
         
        if search_form.created_before.data  != None : 
            query_dict["created__lte"] = search_form.created_before.data 
            
        print search_form.status.data
        print query_dict
        objects = Issue.objects(**query_dict).order_by('-created')
    else:
        objects = Issue.objects.order_by('-created')
    
    search_form.issue_type.choices = [ (obj.id, str(obj)) for obj in IssueType.objects ]
    search_form.status.choices =  [ (obj.id, str(obj)) for obj in IssueStatus.objects ]
    search_form.affected_components.choices =  [ (obj.id, str(obj)) for obj in SoftwareComponent.objects ]
        
    return render_template('find_issues.html', search_form=search_form, issues=objects)

@app.route('/add_issue', methods=['GET','POST'])
def add_issue():
    
    form = IssueForm(request.form)
    if request.method == 'POST':
        if form.validate():
            try:
                print "Issue ? " , request.form["id"]
                issue = Issue.objects.get(id=ObjectId(request.form["id"]))
            except:
                print "Nope "
                issue = Issue()
                
            form.populate_obj(issue)
            issue.save()
        else:
            print "Invalid form " + str(form.errors)
            
    print form
    return redirect(request.referrer)

@app.route('/issue_overview/<issue_id>', methods=['GET','POST'])
def issue_overview(issue_id):
    
    objects = Issue.objects(issue_id=issue_id)
    print objects
    issue = None if len(objects) == 0 else objects[0]
    issue_form = IssueForm(obj=issue)
    
    tests = Test.objects(issues=issue)
    test_form = TestForm()
    test_form.issues.data=[issue]
    
    print "tests " , tests
    return render_template('issue_overview.html', issue=issue, issue_form=issue_form, tests=tests, test_form=test_form)

@app.route('/find_tests', methods=['GET','POST'])    
def find_tests():
    objects= Test.objects().order_by('-test_id')
    return render_template('find_tests.html', tests=objects)

@app.route('/add_test', methods=['GET','POST'])
def add_test():
    
    form = TestForm(request.form)
    if request.method == 'POST':
        if form.validate():
            try:
                print "Existing test? xxxxxxx " , request.form["id"]
                test = Test.objects.get(id=ObjectId(request.form["id"]))
                steps = test.steps
            except:
                print "No new "
                test = Test()
                steps = []
            
            form.populate_obj(test)
            test.steps = steps
            test.save()
            print "Test id " + test.test_id
            print "Saved test: " , test
        else:                
            print "Invalid form " + str(form.errors)

    return redirect(request.referrer)

@app.route('/add_test_step', methods=['GET','POST'])
def add_test_step():
    
    form = TestStepForm(request.form)
    if request.method == 'POST':
        if form.validate():
            try:
                test = Test.objects.get(test_id=form.test_id.data)
                step = TestStep()
                form.populate_obj(step)
                test.steps.append(step)
                test.save()
                
                print "Saved test step for test: " , test
            except:
                print "Failed to save test step"
        else:                
            print "Invalid form ", form.errors
                
    return redirect(request.referrer)

@app.route('/test_overview/<test_id>', methods=['GET','POST'])
def test_overview(test_id):
    
    objects = Test.objects(test_id=test_id)
    print objects
    test = None if len(objects) == 0 else objects[0]
    test_form = TestForm(obj=test)
    test_step_form = TestStepForm()
    test_step_form.test_id.data = test.test_id
    
    return render_template('test_overview.html', test=test, test_form=test_form, test_step_form=test_step_form)


@app.route('/files/<oid>')
def serve_gridfs_file(oid):
    try:
        gfs = GridFS(get_db())
        fl = gfs.get(ObjectId(oid))
        payload = fl.read()
        response = make_response(payload)
        response.mimetype = fl.content_type
        response.headers['Content-Disposition'] = 'attachment; filename='+str(fl.filename)
        return response
    except NoFile:
        abort(404)


@app.route('/delete_file/<test_id>/<oid>')
def delete_gridfs_file(test_id,oid):
    try:
        
        test = Test.objects.get(test_id=test_id)
        for attachment in test.attachments:
            if str(attachment.grid_id) == str(oid):
                del test.attachments[test.attachments.index(attachment)]
                test.save()
        gfs = GridFS(get_db())
        gfs.delete(ObjectId(oid))
        return redirect(request.referrer)
    except NoFile:
        abort(404) 


@app.route('/<test_id>/upload_test_attachment', methods=['POST'])
def upload_test_attachment(test_id):
    if request.method == 'POST':
        test = None
        try:
            test = Test.objects.get(test_id=test_id)
        except:
            print "Error fetching test - "+str(test_id)

        if test != None:
            file = request.files['file']    
            try:
                filename = secure_filename(file.filename)
                test.attachments.append(GridFSProxy())
                test.attachments[-1].put(file,filename = filename, content_type = "application/octet-stream")
                test.save()
                print "File saved"
            except:
                print "Exception in user code:"
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
                print "Error inserting in Database: " + str(filename)
          
    return redirect(request.referrer)
    
@app.route('/find_releases', methods=['GET','POST'])    
def find_releases():
    
    search_form = ReleaseSearchForm(request.form)
    if request.method == 'POST': # and search_form.validate():
        
        query_dict = {}
        print search_form.sw_package.data
        if "sw_package" in request.form and search_form.sw_package.data != u'None': 
            query_dict["package"] = ObjectId(search_form.sw_package.data)
        
        print search_form.device_version.data
        if "device_version" in request.form and search_form.device_version.data != u'None': 
            query_dict["device_version"] = ObjectId(search_form.device_version.data)
        
        print query_dict
        objects= Release.objects(**query_dict).order_by('package', '-major_version',  '-minor_version', '-revision_version')
    else:
        objects= Release.objects().order_by('package', '-major_version',  '-minor_version', '-revision_version')
        
    device_versions = DeviceVersion.objects
    sw_packages = SoftwarePackage.objects
    search_form.sw_package.choices = [ (None, "All") ] + [ (obj.id, str(obj)) for obj in sw_packages ]
    search_form.device_version.choices = [ (None, "All") ] + [ (obj.id, str(obj)) for obj in device_versions ]
    
    return render_template('find_releases.html', search_form=search_form, releases=objects )

@app.route('/release_overview/<package>/<major>/<minor>/<revision>', methods=['GET','POST'])
def release_overview(package,major,minor,revision):
    
    package = SoftwarePackage.objects.get(code=package)
    release = Release.objects.get(package=package, major_version=major, minor_version=minor, revision_version=revision)
    release_form = ReleaseForm(obj=release)
        
    #issues = Issue.objects(implemented_in=release)
    issues = (Issue.objects(implemented_in_aux=release))
    print "rel issues " , issues  
    tests = Test.objects(issues__in=issues)  
    print "rel tests " , tests  
    
    return render_template('release_overview.html', release=release, issues=issues, tests=tests, release_form=release_form)


@app.route('/update_release/<package>/<major>/<minor>/<revision>', methods=['GET','POST'])
def update_release(package, major, minor, revision):
    
    form = ReleaseForm(request.form)
    
    if form.validate():
        package = SoftwarePackage.objects.get(code=package)
        release = Release.objects.get(package=package, major_version=major, minor_version=minor, revision_version=revision)
        print "Updating: ", release
        form.populate_obj(release)
        release.save()
    else:
        print "Form is NOT valid" , form.errors
        
    return redirect(request.referrer)
  

@app.route('/release_report/<package>/<major>/<minor>/<revision>', methods=['GET','POST'])
def release_report(package,major,minor,revision):
    try:
        package = SoftwarePackage.objects.get(code=package)
        release = Release.objects.get(package=package, major_version=major, minor_version=minor, revision_version=revision)
    except:
        abort(404)
        
    issues = Issue.objects(implemented_in_aux=release)
    print "rel issues " , issues  
    tests = Test.objects(issues__in=issues)  
    print "rel tests " , tests  
    return render_template('release_report.html', release=release, issues=issues, tests=tests)

@app.route('/find_bundles', methods=['GET','POST'])    
def find_bundles():
    
    bundles = SoftwareBundle.objects()
    print len(bundles)
    return render_template('find_bundles.html', bundles=bundles)


@app.route('/bundles/<bundle_id>', methods=['GET','POST'])    
def bundle_overview(bundle_id):
    
    bundle = SoftwareBundle.objects.get(id=bundle_id)
    bundle_form = BundleForm(obj=bundle)
    return render_template('bundle_overview.html', bundle=bundle, bundle_form=bundle_form)

@app.route('/add_bundle', methods=['GET','POST'])
def add_bundle():
    
    form = BundleForm(request.form)
    if request.method == 'POST':
        if form.validate():
            try:
                bundle = SoftwareBundle.objects.get(id=ObjectId(request.form["id"]))
            except:
                bundle = SoftwareBundle()
            
            form.populate_obj(bundle)
            bundle.save()
        else:                
            print "Invalid form " + str(form.errors)

    return redirect(request.referrer)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))