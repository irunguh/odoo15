# Author : boniface irungu
# Email: Mwendia.bonface4@gmail.com
#import xmlrpclib
from xmlrpc import client #For python 3 https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
#server url
url = "http://localhost:8069"
#db
db = "whatsapp_kioko"
#username
username = "whatsapp_kioko"
#password
password = "12345"

#login user
common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

#object access
object = client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # Access Object
