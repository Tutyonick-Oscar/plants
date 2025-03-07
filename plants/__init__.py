import pymysql
from django.conf import settings

debug = settings.DEBUG

if not debug:
    pymysql.install_as_MySQLdb()
