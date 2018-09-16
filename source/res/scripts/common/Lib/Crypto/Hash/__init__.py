# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Hash/__init__.py
__all__ = ['HMAC',
 'MD2',
 'MD4',
 'MD5',
 'RIPEMD160',
 'SHA1',
 'SHA224',
 'SHA256',
 'SHA384',
 'SHA512',
 'CMAC']
__revision__ = '$Id$'
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *

def new(algo, *args):
    try:
        new_func = algo.new
    except AttributeError:
        pass
    else:
        return new_func(*args)

    if isinstance(algo, str):
        name = algo
    else:
        try:
            name = algo.name
        except AttributeError:
            raise ValueError('unsupported hash type %r' % (algo,))

    try:
        new_func = _new_funcs[name]
    except KeyError:
        try:
            import hashlib
        except ImportError:
            raise ValueError('unsupported hash type %s' % (name,))

        return hashlib.new(name, *args)

    return new_func(*args)


_new_funcs = {}

def _md2_new(*args):
    from Crypto.Hash import MD2
    _new_funcs['MD2'] = _new_funcs['md2'] = MD2.new
    return MD2.new(*args)


_new_funcs['MD2'] = _new_funcs['md2'] = _md2_new
del _md2_new

def _md4_new(*args):
    from Crypto.Hash import MD4
    _new_funcs['MD4'] = _new_funcs['md4'] = MD4.new
    return MD4.new(*args)


_new_funcs['MD4'] = _new_funcs['md4'] = _md4_new
del _md4_new

def _md5_new(*args):
    from Crypto.Hash import MD5
    _new_funcs['MD5'] = _new_funcs['md5'] = MD5.new
    return MD5.new(*args)


_new_funcs['MD5'] = _new_funcs['md5'] = _md5_new
del _md5_new

def _ripemd160_new(*args):
    from Crypto.Hash import RIPEMD160
    _new_funcs['RIPEMD160'] = _new_funcs['ripemd160'] = _new_funcs['RIPEMD'] = _new_funcs['ripemd'] = RIPEMD160.new
    return RIPEMD160.new(*args)


_new_funcs['RIPEMD160'] = _new_funcs['ripemd160'] = _new_funcs['RIPEMD'] = _new_funcs['ripemd'] = _ripemd160_new
del _ripemd160_new

def _sha1_new(*args):
    from Crypto.Hash import SHA1
    _new_funcs['SHA1'] = _new_funcs['sha1'] = _new_funcs['SHA'] = _new_funcs['sha'] = SHA1.new
    return SHA1.new(*args)


_new_funcs['SHA1'] = _new_funcs['sha1'] = _new_funcs['SHA'] = _new_funcs['sha'] = _sha1_new
del _sha1_new

def _sha224_new(*args):
    from Crypto.Hash import SHA224
    _new_funcs['SHA224'] = _new_funcs['sha224'] = SHA224.new
    return SHA224.new(*args)


_new_funcs['SHA224'] = _new_funcs['sha224'] = _sha224_new
del _sha224_new

def _sha256_new(*args):
    from Crypto.Hash import SHA256
    _new_funcs['SHA256'] = _new_funcs['sha256'] = SHA256.new
    return SHA256.new(*args)


_new_funcs['SHA256'] = _new_funcs['sha256'] = _sha256_new
del _sha256_new

def _sha384_new(*args):
    from Crypto.Hash import SHA384
    _new_funcs['SHA384'] = _new_funcs['sha384'] = SHA384.new
    return SHA384.new(*args)


_new_funcs['SHA384'] = _new_funcs['sha384'] = _sha384_new
del _sha384_new

def _sha512_new(*args):
    from Crypto.Hash import SHA512
    _new_funcs['SHA512'] = _new_funcs['sha512'] = SHA512.new
    return SHA512.new(*args)


_new_funcs['SHA512'] = _new_funcs['sha512'] = _sha512_new
del _sha512_new
