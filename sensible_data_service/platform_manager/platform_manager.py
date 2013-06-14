from utils import service_config
#from utils import EXAMPLE_SECURE_service_config
from .models import *

def authenticate(request):
    print request.method
    print request.GET
    print request.body

    token = request.REQUEST.get('access_token')
    print token

    print request.META['USER']
    print request.user

    host = request.META['REMOTE_ADDR']
    if not host in service_config.PLATFORM['ip_addr']: return {'error': 'ip address not authorized'}

    try: user = AccessToken.objects.get(token=token).user
    except AccessToken.DoesNotExist: return {'error': 'no user found'}

    #TODO: logging
    return {'ok':'authenticated', 'user': user}
