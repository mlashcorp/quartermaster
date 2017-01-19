from apscheduler.schedulers.background import BackgroundScheduler
from models import Release

sched = BackgroundScheduler()
sched.start()

def poll_svn():
    
    print "**poll svn**"
    releases = Release.objects()
    
    for release in release:
        print "Checking svn log for ", release
    
    #"svn log -v --stop-on-copy http://subversion.repository.com/svn/repositoryname"
    

sched.add_job(poll_svn, 'interval', minutes=1)
