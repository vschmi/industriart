"""
Access JFrog's Artifactory from Python
"""

import logging
from .compat import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
