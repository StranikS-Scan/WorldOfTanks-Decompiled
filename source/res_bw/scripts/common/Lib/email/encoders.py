# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/encoders.py
"""Encodings and related functions."""
__all__ = ['encode_7or8bit',
 'encode_base64',
 'encode_noop',
 'encode_quopri']
import base64
from quopri import encodestring as _encodestring

def _qencode(s):
    enc = _encodestring(s, quotetabs=True)
    return enc.replace(' ', '=20')


def _bencode(s):
    if not s:
        return s
    hasnewline = s[-1] == '\n'
    value = base64.encodestring(s)
    return value[:-1] if not hasnewline and value[-1] == '\n' else value


def encode_base64(msg):
    """Encode the message's payload in Base64.
    
    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload()
    encdata = _bencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'base64'


def encode_quopri(msg):
    """Encode the message's payload in quoted-printable.
    
    Also, add an appropriate Content-Transfer-Encoding header.
    """
    orig = msg.get_payload()
    encdata = _qencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'quoted-printable'


def encode_7or8bit(msg):
    """Set the Content-Transfer-Encoding header to 7bit or 8bit."""
    orig = msg.get_payload()
    if orig is None:
        msg['Content-Transfer-Encoding'] = '7bit'
        return
    else:
        try:
            orig.encode('ascii')
        except UnicodeError:
            msg['Content-Transfer-Encoding'] = '8bit'
        else:
            msg['Content-Transfer-Encoding'] = '7bit'

        return


def encode_noop(msg):
    """Do nothing."""
    pass
