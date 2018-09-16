# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/IO/_PBES.py
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto import Random
from Crypto.Util.asn1 import *
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import MD5, SHA1
from Crypto.Cipher import DES, ARC2, DES3, AES
from Crypto.Protocol.KDF import PBKDF1, PBKDF2

def decode_der(obj_class, binstr):
    der = obj_class()
    der.decode(binstr)
    return der


class PBES1(object):

    def decrypt(data, passphrase):
        encrypted_private_key_info = decode_der(DerSequence, data)
        encrypted_algorithm = decode_der(DerSequence, encrypted_private_key_info[0])
        encrypted_data = decode_der(DerOctetString, encrypted_private_key_info[1]).payload
        pbe_oid = decode_der(DerObjectId, encrypted_algorithm[0]).value
        cipher_params = {}
        if pbe_oid == '1.2.840.113549.1.5.3':
            hashmod = MD5
            ciphermod = DES
        elif pbe_oid == '1.2.840.113549.1.5.6':
            hashmod = MD5
            ciphermod = ARC2
            cipher_params['effective_keylen'] = 64
        elif pbe_oid == '1.2.840.113549.1.5.10':
            hashmod = SHA1
            ciphermod = DES
        elif pbe_oid == '1.2.840.113549.1.5.11':
            hashmod = SHA1
            ciphermod = ARC2
            cipher_params['effective_keylen'] = 64
        else:
            raise ValueError('Unknown OID')
        pbe_params = decode_der(DerSequence, encrypted_algorithm[1])
        salt = decode_der(DerOctetString, pbe_params[0]).payload
        iterations = pbe_params[1]
        key_iv = PBKDF1(passphrase, salt, 16, iterations, hashmod)
        key, iv = key_iv[:8], key_iv[8:]
        cipher = ciphermod.new(key, ciphermod.MODE_CBC, iv, **cipher_params)
        pt = cipher.decrypt(encrypted_data)
        return unpad(pt, cipher.block_size)

    decrypt = staticmethod(decrypt)


class PBES2(object):

    def encrypt(data, passphrase, protection, prot_params=None, randfunc=None):
        if prot_params is None:
            prot_params = {}
        if randfunc is None:
            randfunc = Random.new().read
        if protection == 'PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC':
            key_size = 24
            module = DES3
            protection = DES3.MODE_CBC
            enc_oid = '1.2.840.113549.3.7'
        elif protection == 'PBKDF2WithHMAC-SHA1AndAES128-CBC':
            key_size = 16
            module = AES
            protection = AES.MODE_CBC
            enc_oid = '2.16.840.1.101.3.4.1.2'
        elif protection == 'PBKDF2WithHMAC-SHA1AndAES192-CBC':
            key_size = 24
            module = AES
            protection = AES.MODE_CBC
            enc_oid = '2.16.840.1.101.3.4.1.22'
        elif protection == 'PBKDF2WithHMAC-SHA1AndAES256-CBC':
            key_size = 32
            module = AES
            protection = AES.MODE_CBC
            enc_oid = '2.16.840.1.101.3.4.1.42'
        else:
            raise ValueError('Unknown mode')
        iv = randfunc(module.block_size)
        salt = randfunc(prot_params.get('salt_size', 8))
        count = prot_params.get('iteration_count', 1000)
        key = PBKDF2(passphrase, salt, key_size, count)
        key_derivation_func = newDerSequence(DerObjectId('1.2.840.113549.1.5.12'), newDerSequence(DerOctetString(salt), DerInteger(count)))
        cipher = module.new(key, protection, iv)
        encrypted_data = cipher.encrypt(pad(data, cipher.block_size))
        encryption_scheme = newDerSequence(DerObjectId(enc_oid), DerOctetString(iv))
        encrypted_private_key_info = newDerSequence(newDerSequence(DerObjectId('1.2.840.113549.1.5.13'), newDerSequence(key_derivation_func, encryption_scheme)), DerOctetString(encrypted_data))
        return encrypted_private_key_info.encode()

    encrypt = staticmethod(encrypt)

    def decrypt(data, passphrase):
        encrypted_private_key_info = decode_der(DerSequence, data)
        encryption_algorithm = decode_der(DerSequence, encrypted_private_key_info[0])
        encrypted_data = decode_der(DerOctetString, encrypted_private_key_info[1]).payload
        pbe_oid = decode_der(DerObjectId, encryption_algorithm[0]).value
        if pbe_oid != '1.2.840.113549.1.5.13':
            raise ValueError('Not a PBES2 object')
        pbes2_params = decode_der(DerSequence, encryption_algorithm[1])
        key_derivation_func = decode_der(DerSequence, pbes2_params[0])
        key_derivation_oid = decode_der(DerObjectId, key_derivation_func[0]).value
        if key_derivation_oid != '1.2.840.113549.1.5.12':
            raise ValueError('Unknown KDF')
        pbkdf2_params = decode_der(DerSequence, key_derivation_func[1])
        salt = decode_der(DerOctetString, pbkdf2_params[0]).payload
        iteration_count = pbkdf2_params[1]
        if len(pbkdf2_params) > 2:
            pbkdf2_key_length = pbkdf2_params[2]
        else:
            pbkdf2_key_length = None
        if len(pbkdf2_params) > 3:
            raise ValueError('Unsupported PRF for PBKDF2')
        encryption_scheme = decode_der(DerSequence, pbes2_params[1])
        encryption_oid = decode_der(DerObjectId, encryption_scheme[0]).value
        if encryption_oid == '1.2.840.113549.3.7':
            ciphermod = DES3
            key_size = 24
        elif encryption_oid == '2.16.840.1.101.3.4.1.2':
            ciphermod = AES
            key_size = 16
        elif encryption_oid == '2.16.840.1.101.3.4.1.22':
            ciphermod = AES
            key_size = 24
        elif encryption_oid == '2.16.840.1.101.3.4.1.42':
            ciphermod = AES
            key_size = 32
        else:
            raise ValueError('Unsupported cipher')
        if pbkdf2_key_length and pbkdf2_key_length != key_size:
            raise ValueError('Mismatch between PBKDF2 parameters and selected cipher')
        IV = decode_der(DerOctetString, encryption_scheme[1]).payload
        key = PBKDF2(passphrase, salt, key_size, iteration_count)
        cipher = ciphermod.new(key, ciphermod.MODE_CBC, IV)
        pt = cipher.decrypt(encrypted_data)
        return unpad(pt, cipher.block_size)

    decrypt = staticmethod(decrypt)
