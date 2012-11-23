
__version_info__ = (0, 0, 1)
__version__ = '.'.join(map(str,__version_info__))

from flask import Flask
app = Flask(__name__)

import torouterui.views
