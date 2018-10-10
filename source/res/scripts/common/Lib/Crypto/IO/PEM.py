# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/IO/PEM.py
__all__ = ['encode', 'decode']
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
import re
from binascii import hexlify, unhexlify, a2b_base64, b2a_base64
from Crypto.Hash import MD5
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import DES, DES3, AES
from Crypto.Protocol.KDF import PBKDF1
from Crypto.Random import get_random_bytes

def encode(data, marker, passphrase=None, randfunc=None):
    if randfunc is None:
        randfunc = get_random_bytes
    out = '-----BEGIN %s-----\n' % marker
    if passphrase:
        salt = randfunc(8)
        key = PBKDF1(passphrase, salt, 16, 1, MD5)
        key += PBKDF1(key + passphrase, salt, 8, 1, MD5)
        objenc = DES3.new(key, DES3.MODE_CBC, salt)
        out += 'Proc-Type: 4,ENCRYPTED\nDEK-Info: DES-EDE3-CBC,%s\n\n' % tostr(hexlify(salt).upper())
        data = objenc.encrypt(pad(data, objenc.block_size))
    chunks = [ tostr(b2a_base64(data[i:i + 48])) for i in range(0, len(data), 48) ]
    out += ''.join(chunks)
    out += '-----END %s-----' % marker
    return out


def decode(pem_data, passphrase=None):
    r = re.compile('\\s*-----BEGIN (.*)-----\n')
    m = r.match(pem_data)
    if not m:
        raise ValueError('Not a valid PEM pre boundary')
    marker = m.group(1)
    r = re.compile('-----END (.*)-----\\s*$')
    m = r.search(pem_data)
    if not m or m.group(1) != marker:
        raise ValueError('Not a valid PEM post boundary')
    lines = pem_data.replace(' ', '').split()
    if lines[1].startswith('Proc-Type:4,ENCRYPTED'):
        if not passphrase:
            raise ValueError('PEM is encrypted, but no passphrase available')
        DEK = lines[2].split(':')
        if len(DEK) != 2 or DEK[0] != 'DEK-Info':
            raise ValueError('PEM encryption format not supported.')
        algo, salt = DEK[1].split(',')
        salt = unhexlify(tobytes(salt))
        if algo == 'DES-CBC':
            key = PBKDF1(passphrase, salt, 8, 1, MD5)
            objdec = DES.new(key, DES.MODE_CBC, salt)
        elif algo == 'DES-EDE3-CBC':
            key = PBKDF1(passphrase, salt, 16, 1, MD5)
            key += PBKDF1(key + passphrase, salt, 8, 1, MD5)
            objdec = DES3.new(key, DES3.MODE_CBC, salt)
        elif algo == 'AES-128-CBC':
            key = PBKDF1(passphrase, salt[:8], 16, 1, MD5)
            objdec = AES.new(key, AES.MODE_CBC, salt)
        else:
            raise ValueError('Unsupport PEM encryption algorithm.')
        lines = lines[2:]
    else:
        objdec = None
    data = a2b_base64(b(''.join(lines[1:-1])))
    enc_flag = False
    if objdec:
        data = unpad(objdec.decrypt(data), objdec.block_size)
        enc_flag = True
    return (data, marker, enc_flag)
