# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/mime/nonmultipart.py
# Compiled at: 2010-05-25 20:46:16
"""Base class for MIME type messages that are not multipart."""
__all__ = ['MIMENonMultipart']
from email import errors
from email.mime.base import MIMEBase

class MIMENonMultipart(MIMEBase):
    """Base class for MIME multipart/* type messages."""
    __pychecker__ = 'unusednames=payload'

    def attach(self, payload):
        raise errors.MultipartConversionError('Cannot attach additional subparts to non-multipart/*')

    del __pychecker__
