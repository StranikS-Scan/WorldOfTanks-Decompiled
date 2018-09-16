# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/encoders.py
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
    orig = msg.get_payload()
    encdata = _bencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'base64'


def encode_quopri(msg):
    orig = msg.get_payload()
    encdata = _qencode(orig)
    msg.set_payload(encdata)
    msg['Content-Transfer-Encoding'] = 'quoted-printable'


def encode_7or8bit(msg):
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
    pass
