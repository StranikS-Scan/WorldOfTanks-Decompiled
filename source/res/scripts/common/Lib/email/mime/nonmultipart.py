# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/mime/nonmultipart.py
__all__ = ['MIMENonMultipart']
from email import errors
from email.mime.base import MIMEBase

class MIMENonMultipart(MIMEBase):

    def attach(self, payload):
        raise errors.MultipartConversionError('Cannot attach additional subparts to non-multipart/*')
