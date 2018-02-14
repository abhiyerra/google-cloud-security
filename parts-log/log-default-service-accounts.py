from googleapiclient import discovery
import os
import logging
from logging.handlers import RotatingFileHandler
from gcp import get_key, get_projects

# logs all Default Service Accounts from the Service Account page

if os.path.isfile(get_key()):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_key()

alert = False

path = os.path.expanduser('~/python-logs')
logfile = os.path.expanduser('~/python-logs/security.log')

if os.path.isdir(path):
    pass
else:
    os.mkdir(path)


logger = logging.getLogger("Rotating Log")
log_formatter = logging.Formatter('%(asctime)s\t %(levelname)s %(message)s')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(log_formatter)
logger.addHandler(handler)

for project in get_projects():
    project_name = 'projects/' + project
    service = discovery.build('iam', 'v1')
    request = service.projects().serviceAccounts().list(name=project_name)
    response = request.execute()

    try:
        accounts = response['accounts']

        for account in accounts:
            serviceaccount = account['email']

            if 'gserviceaccount.com' in serviceaccount and 'iam' not in serviceaccount:
                alert = True
                logger.warning('Default Service Account "{0}" found in project "{1}"'.
                               format(serviceaccount, project))
    except KeyError:
        logger.info('0 Service Accounts available in project "{0}"'.format(project))

    except Exception:
        logger.error('Default Service Account - Unknown Error!  Please run manually')

if alert is False:
    logger.info('No Default Service Accounts found')
