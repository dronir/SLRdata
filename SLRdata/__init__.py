
__title__ = 'my_package'
__version__ = '0.1'
__author__ = 'Your Name'
__license__ = 'Some License'

import requests

def foofoo():
    r = requests.get('http://python.org/')
    print(r.status_code)
