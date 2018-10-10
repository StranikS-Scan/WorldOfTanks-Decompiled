# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/IO/PKCS8.py
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto.Util.asn1 import *
from Crypto.IO._PBES import PBES1, PBES2
__all__ = ['wrap', 'unwrap']

def decode_der(obj_class, binstr):
    der = obj_class()
    der.decode(binstr)
    return der


def wrap(private_key, key_oid, passphrase=None, protection=None, prot_params=None, key_params=None, randfunc=None):
    if key_params is None:
        key_params = DerNull()
    pk_info = newDerSequence(0, newDerSequence(DerObjectId(key_oid), key_params), newDerOctetString(private_key))
    pk_info_der = pk_info.encode()
    if not passphrase:
        return pk_info_der
    else:
        passphrase = tobytes(passphrase)
        if protection is None:
            protection = 'PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC'
        return PBES2.encrypt(pk_info_der, passphrase, protection, prot_params, randfunc)


def unwrap(p8_private_key, passphrase=None):
    if passphrase:
        passphrase = tobytes(passphrase)
        found = False
        for pbes in (PBES1, PBES2):
            try:
                p8_private_key = pbes.decrypt(p8_private_key, passphrase)
            except ValueError:
                pass
            else:
                found = True
                break

        if not found:
            raise ValueError('Unsupported PKCS#5 Object ID ')
    pk_info = decode_der(DerSequence, p8_private_key)
    if len(pk_info) == 2 and not passphrase:
        raise ValueError('Not a valid clear PKCS#8 structure (maybe it is encrypted?)')
    if not 3 <= len(pk_info) <= 4 or pk_info[0] != 0:
        raise ValueError('Not a valid PrivateKeyInfo SEQUENCE')
    algo_id = decode_der(DerSequence, pk_info[1])
    if not 1 <= len(algo_id) <= 2:
        raise ValueError('Not a valid AlgorithmIdentifier SEQUENCE')
    algo = decode_der(DerObjectId, algo_id[0]).value
    private_key = decode_der(DerOctetString, pk_info[2]).payload
    if len(algo_id) == 2 and algo_id[1] != b('\x05\x00'):
        params = algo_id[1]
    else:
        params = None
    return (algo, private_key, params)
