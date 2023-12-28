#import xmlrpclib

from xmlrpc import client #For python 3 https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client

#server url
#url = "https://marketing.amkatek.com"
url = "http://localhost:8069"
#db
db = "discipleship_15"
# #username
# username = "admin"
# #password
# password = "@gdc@2021@"

# mobile app user
#username
#username = "apiuser@amkatek.com"
username="admin"
password="12345"
#password
#password = "api!#@2022"

#login user
common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

#object access
object = client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # Access Object
