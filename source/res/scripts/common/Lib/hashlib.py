# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/hashlib.py
r"""hashlib module - A common interface to many hash functions.

new(name, string='') - returns a new hash object implementing the
                       given hash function; initializing the hash
                       using the given string data.

Named constructor functions are also available, these are much faster
than using new():

md5(), sha1(), sha224(), sha256(), sha384(), and sha512()

More algorithms may be available on your platform but the above are
guaranteed to exist.

NOTE: If you want the adler32 or crc32 hash functions they are available in
the zlib module.

Choose your hash function wisely.  Some have known collision weaknesses.
sha384 and sha512 will be slow on 32 bit platforms.

Hash objects have these methods:
 - update(arg): Update the hash object with the string arg. Repeated calls
                are equivalent to a single call with the concatenation of all
                the arguments.
 - digest():    Return the digest of the strings passed to the update() method
                so far. This may contain non-ASCII characters, including
                NUL bytes.
 - hexdigest(): Like digest() except the digest is returned as a string of
                double length, containing only hexadecimal digits.
 - copy():      Return a copy (clone) of the hash object. This can be used to
                efficiently compute the digests of strings that share a common
                initial substring.

For example, to obtain the digest of the string 'Nobody inspects the
spammish repetition':

    >>> import hashlib
    >>> m = hashlib.md5()
    >>> m.update("Nobody inspects")
    >>> m.update(" the spammish repetition")
    >>> m.digest()
    '\xbbd\x9c\x83\xdd\x1e\xa5\xc9\xd9\xde\xc9\xa1\x8d\xf0\xff\xe9'

More condensed:

    >>> hashlib.sha224("Nobody inspects the spammish repetition").hexdigest()
    'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2'

"""
__always_supported = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
algorithms = __always_supported
__all__ = __always_supported + ('new', 'algorithms')

def __get_builtin_constructor(name):
    try:
        if name in ('SHA1', 'sha1'):
            import _sha
            return _sha.new
        if name in ('MD5', 'md5'):
            import _md5
            return _md5.new
        if name in ('SHA256', 'sha256', 'SHA224', 'sha224'):
            import _sha256
            bs = name[3:]
            if bs == '256':
                return _sha256.sha256
            if bs == '224':
                return _sha256.sha224
        elif name in ('SHA512', 'sha512', 'SHA384', 'sha384'):
            import _sha512
            bs = name[3:]
            if bs == '512':
                return _sha512.sha512
            if bs == '384':
                return _sha512.sha384
    except ImportError:
        pass

    raise ValueError('unsupported hash type ' + name)


def __get_openssl_constructor(name):
    try:
        f = getattr(_hashlib, 'openssl_' + name)
        f()
        return f
    except (AttributeError, ValueError):
        return __get_builtin_constructor(name)


def __py_new(name, string=''):
    return __get_builtin_constructor(name)(string)


def __hash_new(name, string=''):
    try:
        return _hashlib.new(name, string)
    except ValueError:
        return __get_builtin_constructor(name)(string)


try:
    import _hashlib
    new = __hash_new
    __get_hash = __get_openssl_constructor
except ImportError:
    new = __py_new
    __get_hash = __get_builtin_constructor

for __func_name in __always_supported:
    try:
        globals()[__func_name] = __get_hash(__func_name)
    except ValueError:
        import logging
        logging.exception('code for hash %s was not found.', __func_name)

del __always_supported
del __func_name
del __get_hash
del __py_new
del __hash_new
del __get_openssl_constructor
