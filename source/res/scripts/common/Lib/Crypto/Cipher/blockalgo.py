# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/blockalgo.py
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from binascii import unhexlify
from Crypto.Util import Counter
from Crypto.Util.strxor import strxor
from Crypto.Util import galois
from Crypto.Util.number import long_to_bytes, bytes_to_long
import Crypto.Util.Counter
from Crypto.Hash import CMAC
from Crypto.Hash.CMAC import _SmoothMAC
from Crypto.Protocol.KDF import _S2V
MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_CCM = 8
MODE_EAX = 9
MODE_SIV = 10
MODE_GCM = 11

def _getParameter(name, index, args, kwargs, default=None):
    param = kwargs.get(name)
    if len(args) > index:
        if param:
            raise TypeError("Parameter '%s' is specified twice" % name)
        param = args[index]
    return param or default


class _CBCMAC(_SmoothMAC):

    def __init__(self, key, ciphermod):
        _SmoothMAC.__init__(self, ciphermod.block_size, None, 0)
        self._key = key
        self._factory = ciphermod
        return

    def _ignite(self, data):
        if self._mac:
            raise TypeError('_ignite() cannot be called twice')
        self._buffer.insert(0, data)
        self._buffer_len += len(data)
        self._mac = self._factory.new(self._key, MODE_CBC, bchr(0) * 16)
        self.update(b(''))

    def _update(self, block_data):
        self._t = self._mac.encrypt(block_data)[-16:]

    def _digest(self, left_data):
        return self._t


class _GHASH(_SmoothMAC):

    def __init__(self, hash_subkey, block_size):
        _SmoothMAC.__init__(self, block_size, None, 0)
        self._hash_subkey = _galois.ghash_expand(hash_subkey)
        self._last_y = bchr(0) * 16
        self._mac = _galois.ghash
        return

    def copy(self):
        clone = _GHASH(self._hash_subkey, self._bs)
        _SmoothMAC._deep_copy(self, clone)
        clone._last_y = self._last_y
        return clone

    def _update(self, block_data):
        self._last_y = _galois.ghash(block_data, self._last_y, self._hash_subkey)

    def _digest(self, left_data):
        return self._last_y


class BlockAlgo:

    def __init__(self, factory, key, *args, **kwargs):
        self.mode = _getParameter('mode', 0, args, kwargs, default=MODE_ECB)
        self.block_size = factory.block_size
        self._factory = factory
        self._tag = None
        if self.mode == MODE_CCM:
            if self.block_size != 16:
                raise TypeError('CCM mode is only available for ciphers that operate on 128 bits blocks')
            self._mac_len = kwargs.get('mac_len', 16)
            if self._mac_len not in (4, 6, 8, 10, 12, 14, 16):
                raise ValueError("Parameter 'mac_len' must be even and in the range 4..16")
            self.nonce = _getParameter('nonce', 1, args, kwargs)
            if not (self.nonce and 7 <= len(self.nonce) <= 13):
                raise ValueError("Length of parameter 'nonce' must be in the range 7..13 bytes")
            self._key = key
            self._msg_len = kwargs.get('msg_len', None)
            self._assoc_len = kwargs.get('assoc_len', None)
            self._cipherMAC = _CBCMAC(key, factory)
            self._done_assoc_data = False
            self._next = [self.update,
             self.encrypt,
             self.decrypt,
             self.digest,
             self.verify]
            self._start_ccm()
        elif self.mode == MODE_OPENPGP:
            self._start_PGP(factory, key, *args, **kwargs)
        elif self.mode == MODE_EAX:
            self._start_eax(factory, key, *args, **kwargs)
        elif self.mode == MODE_SIV:
            self._start_siv(factory, key, *args, **kwargs)
        elif self.mode == MODE_GCM:
            self._start_gcm(factory, key, *args, **kwargs)
        else:
            self._cipher = factory.new(key, *args, **kwargs)
            self.IV = self._cipher.IV
        return

    def _start_gcm(self, factory, key, *args, **kwargs):
        if self.block_size != 16:
            raise TypeError('GCM mode is only available for ciphers that operate on 128 bits blocks')
        self.nonce = _getParameter('nonce', 1, args, kwargs)
        if not self.nonce:
            raise TypeError('MODE_GCM requires a nonce')
        self._mac_len = kwargs.get('mac_len', 16)
        if not (self._mac_len and 4 <= self._mac_len <= 16):
            raise ValueError("Parameter 'mac_len' must not be larger than 16 bytes")
        self._next = [self.update,
         self.encrypt,
         self.decrypt,
         self.digest,
         self.verify]
        self._done_assoc_data = False
        self._msg_len = 0
        hash_subkey = factory.new(key).encrypt(bchr(0) * 16)
        if len(self.nonce) == 12:
            self._j0 = bytes_to_long(self.nonce + b('\x00\x00\x00\x01'))
        else:
            fill = (16 - len(self.nonce) % 16) % 16 + 8
            ghash_in = self.nonce + bchr(0) * fill + long_to_bytes(8 * len(self.nonce), 8)
            mac = _GHASH(hash_subkey, factory.block_size)
            mac.update(ghash_in)
            self._j0 = bytes_to_long(mac.digest())
        ctr = Counter.new(128, initial_value=self._j0 + 1, allow_wraparound=True)
        self._cipher = self._factory.new(key, MODE_CTR, counter=ctr)
        self._cipherMAC = _GHASH(hash_subkey, factory.block_size)
        ctr = Counter.new(128, initial_value=self._j0, allow_wraparound=True)
        self._tag_cipher = self._factory.new(key, MODE_CTR, counter=ctr)

    def _start_siv(self, factory, key, *args, **kwargs):
        subkey_size, rem = divmod(len(key), 2)
        if rem:
            raise ValueError('MODE_SIV requires a key twice as long as for the underlying cipher')
        self.nonce = _getParameter('nonce', 1, args, kwargs)
        self._cipherMAC = _S2V(key[:subkey_size], ciphermod=factory)
        self._subkey_ctr = key[subkey_size:]
        self._mac_len = factory.block_size
        self._cipherMAC = self._cipherMAC
        self._next = [self.update,
         self.encrypt,
         self.decrypt,
         self.digest,
         self.verify]

    def _siv_ctr_cipher(self, tag):
        tag_int = bytes_to_long(tag)
        init_counter = tag_int ^ tag_int & 9223372039002259456L
        ctr = Counter.new(self._factory.block_size * 8, initial_value=init_counter, allow_wraparound=True)
        return self._factory.new(self._subkey_ctr, MODE_CTR, counter=ctr)

    def _start_eax(self, factory, key, *args, **kwargs):
        self.nonce = _getParameter('nonce', 1, args, kwargs)
        if not self.nonce:
            raise TypeError('MODE_EAX requires a nonce')
        self._next = [self.update,
         self.encrypt,
         self.decrypt,
         self.digest,
         self.verify]
        self._mac_len = kwargs.get('mac_len', self.block_size)
        if not (self._mac_len and 4 <= self._mac_len <= self.block_size):
            raise ValueError("Parameter 'mac_len' must not be larger than %d" % self.block_size)
        self._omac = [ CMAC.new(key, bchr(0) * (self.block_size - 1) + bchr(i), ciphermod=factory) for i in xrange(0, 3) ]
        self._omac[0].update(self.nonce)
        self._cipherMAC = self._omac[1]
        counter_int = bytes_to_long(self._omac[0].digest())
        counter_obj = Crypto.Util.Counter.new(self.block_size * 8, initial_value=counter_int, allow_wraparound=True)
        self._cipher = factory.new(key, MODE_CTR, counter=counter_obj)

    def _start_PGP(self, factory, key, *args, **kwargs):
        self._done_first_block = False
        self._done_last_block = False
        self.IV = _getParameter('IV', 1, args, kwargs)
        if self.IV is None:
            self.IV = _getParameter('iv', 1, args, kwargs)
        if not self.IV:
            raise ValueError('MODE_OPENPGP requires an IV')
        IV_cipher = factory.new(key, MODE_CFB, b('\x00') * self.block_size, segment_size=self.block_size * 8)
        if len(self.IV) == self.block_size:
            self._encrypted_IV = IV_cipher.encrypt(self.IV + self.IV[-2:] + b('\x00') * (self.block_size - 2))[:self.block_size + 2]
        elif len(self.IV) == self.block_size + 2:
            self._encrypted_IV = self.IV
            self.IV = IV_cipher.decrypt(self.IV + b('\x00') * (self.block_size - 2))[:self.block_size + 2]
            if self.IV[-2:] != self.IV[-4:-2]:
                raise ValueError('Failed integrity check for OPENPGP IV')
            self.IV = self.IV[:-2]
        else:
            raise ValueError('Length of IV must be %d or %d bytes for MODE_OPENPGP' % (self.block_size, self.block_size + 2))
        self._cipher = factory.new(key, MODE_CFB, self._encrypted_IV[-self.block_size:], segment_size=self.block_size * 8)
        return

    def _start_ccm(self, assoc_len=None, msg_len=None):
        if self._cipherMAC.can_reduce():
            return
        else:
            if assoc_len is not None:
                self._assoc_len = assoc_len
            if msg_len is not None:
                self._msg_len = msg_len
            if None in (self._assoc_len, self._msg_len):
                return
            q = 15 - len(self.nonce)
            flags = 64 * (self._assoc_len > 0) + 8 * divmod(self._mac_len - 2, 2)[0] + (q - 1)
            b_0 = bchr(flags) + self.nonce + long_to_bytes(self._msg_len, q)
            assoc_len_encoded = b('')
            if self._assoc_len > 0:
                if self._assoc_len < 65536 - 256:
                    enc_size = 2
                elif self._assoc_len < 4294967296L:
                    assoc_len_encoded = b('\xff\xfe')
                    enc_size = 4
                else:
                    assoc_len_encoded = b('\xff\xff')
                    enc_size = 8
                assoc_len_encoded += long_to_bytes(self._assoc_len, enc_size)
            self._cipherMAC._ignite(b_0 + assoc_len_encoded)
            prefix = bchr(q - 1) + self.nonce
            ctr = Counter.new(128 - len(prefix) * 8, prefix, initial_value=0)
            self._cipher = self._factory.new(self._key, MODE_CTR, counter=ctr)
            self._s_0 = self._cipher.encrypt(bchr(0) * 16)
            return

    def update(self, assoc_data):
        if self.mode not in (MODE_CCM,
         MODE_EAX,
         MODE_SIV,
         MODE_GCM):
            raise TypeError('update() not supported by this mode of operation')
        if self.update not in self._next:
            raise TypeError('update() can only be called immediately after initialization')
        self._next = [self.update,
         self.encrypt,
         self.decrypt,
         self.digest,
         self.verify]
        return self._cipherMAC.update(assoc_data)

    def encrypt(self, plaintext):
        if self.mode == MODE_OPENPGP:
            padding_length = (self.block_size - len(plaintext) % self.block_size) % self.block_size
            if padding_length > 0:
                if self._done_last_block:
                    raise ValueError('Only the last chunk is allowed to have length not multiple of %d bytes', self.block_size)
                self._done_last_block = True
                padded = plaintext + b('\x00') * padding_length
                res = self._cipher.encrypt(padded)[:len(plaintext)]
            else:
                res = self._cipher.encrypt(plaintext)
            if not self._done_first_block:
                res = self._encrypted_IV + res
                self._done_first_block = True
            return res
        else:
            if self.mode in (MODE_CCM,
             MODE_EAX,
             MODE_SIV,
             MODE_GCM):
                if self.encrypt not in self._next:
                    raise TypeError('encrypt() can only be called after initialization or an update()')
                self._next = [self.encrypt, self.digest]
            if self.mode == MODE_CCM:
                if self._assoc_len is None:
                    self._start_ccm(assoc_len=self._cipherMAC.get_len())
                if self._msg_len is None:
                    self._start_ccm(msg_len=len(plaintext))
                    self._next = [self.digest]
                if not self._done_assoc_data:
                    self._cipherMAC.zero_pad()
                    self._done_assoc_data = True
                self._cipherMAC.update(plaintext)
            if self.mode == MODE_SIV:
                self._next = [self.digest]
                if self.nonce:
                    self._cipherMAC.update(self.nonce)
                self._cipherMAC.update(plaintext)
                self._cipher = self._siv_ctr_cipher(self._cipherMAC.derive())
            ct = self._cipher.encrypt(plaintext)
            if self.mode == MODE_EAX:
                self._omac[2].update(ct)
            if self.mode == MODE_GCM:
                if not self._done_assoc_data:
                    self._cipherMAC.zero_pad()
                    self._done_assoc_data = True
                self._cipherMAC.update(ct)
                self._msg_len += len(plaintext)
            return ct

    def decrypt(self, ciphertext):
        if self.mode == MODE_OPENPGP:
            padding_length = (self.block_size - len(ciphertext) % self.block_size) % self.block_size
            if padding_length > 0:
                if self._done_last_block:
                    raise ValueError('Only the last chunk is allowed to have length not multiple of %d bytes', self.block_size)
                self._done_last_block = True
                padded = ciphertext + b('\x00') * padding_length
                res = self._cipher.decrypt(padded)[:len(ciphertext)]
            else:
                res = self._cipher.decrypt(ciphertext)
            return res
        else:
            if self.mode == MODE_SIV:
                raise TypeError('decrypt() not allowed for SIV mode. Use decrypt_and_verify() instead.')
            if self.mode in (MODE_CCM, MODE_EAX, MODE_GCM):
                if self.decrypt not in self._next:
                    raise TypeError('decrypt() can only be called after initialization or an update()')
                self._next = [self.decrypt, self.verify]
                if self.mode == MODE_CCM:
                    if self._assoc_len is None:
                        self._start_ccm(assoc_len=self._cipherMAC.get_len())
                    if self._msg_len is None:
                        self._start_ccm(msg_len=len(ciphertext))
                        self._next = [self.verify]
                    if not self._done_assoc_data:
                        self._cipherMAC.zero_pad()
                        self._done_assoc_data = True
                if self.mode == MODE_GCM:
                    if not self._done_assoc_data:
                        self._cipherMAC.zero_pad()
                        self._done_assoc_data = True
                    self._cipherMAC.update(ciphertext)
                    self._msg_len += len(ciphertext)
                if self.mode == MODE_EAX:
                    self._omac[2].update(ciphertext)
            pt = self._cipher.decrypt(ciphertext)
            if self.mode == MODE_CCM:
                self._cipherMAC.update(pt)
            return pt

    def digest(self):
        if self.mode not in (MODE_CCM,
         MODE_EAX,
         MODE_SIV,
         MODE_GCM):
            raise TypeError('digest() not supported by this mode of operation')
        if self.digest not in self._next:
            raise TypeError('digest() cannot be called when decrypting or validating a message')
        self._next = [self.digest]
        return self._compute_mac()

    def _compute_mac(self):
        if self._tag:
            return self._tag
        else:
            if self.mode == MODE_CCM:
                if self._assoc_len is None:
                    self._start_ccm(assoc_len=self._cipherMAC.get_len())
                if self._msg_len is None:
                    self._start_ccm(msg_len=0)
                self._cipherMAC.zero_pad()
                self._tag = strxor(self._cipherMAC.digest(), self._s_0)[:self._mac_len]
            if self.mode == MODE_GCM:
                self._cipherMAC.zero_pad()
                auth_len = self._cipherMAC.get_len() - self._msg_len
                for tlen in (auth_len, self._msg_len):
                    self._cipherMAC.update(long_to_bytes(8 * tlen, 8))

                s_tag = self._cipherMAC.digest()
                self._tag = self._tag_cipher.encrypt(s_tag)[:self._mac_len]
            if self.mode == MODE_EAX:
                tag = bchr(0) * self.block_size
                for i in xrange(3):
                    tag = strxor(tag, self._omac[i].digest())

                self._tag = tag[:self._mac_len]
            if self.mode == MODE_SIV:
                self._tag = self._cipherMAC.derive()
            return self._tag

    def hexdigest(self):
        return ''.join([ '%02x' % bord(x) for x in self.digest() ])

    def verify(self, mac_tag):
        if self.mode not in (MODE_CCM,
         MODE_EAX,
         MODE_SIV,
         MODE_GCM):
            raise TypeError('verify() not supported by this mode of operation')
        if self.verify not in self._next:
            raise TypeError('verify() cannot be called when encrypting a message')
        self._next = [self.verify]
        res = 0
        for x, y in zip(self._compute_mac(), mac_tag):
            res |= bord(x) ^ bord(y)

        if res or len(mac_tag) != self._mac_len:
            raise ValueError('MAC check failed')

    def hexverify(self, hex_mac_tag):
        self.verify(unhexlify(hex_mac_tag))

    def encrypt_and_digest(self, plaintext):
        return (self.encrypt(plaintext), self.digest())

    def decrypt_and_verify(self, ciphertext, mac_tag):
        if self.mode == MODE_SIV:
            if self.decrypt not in self._next:
                raise TypeError('decrypt() can only be called after initialization or an update()')
            self._next = [self.verify]
            self._mac = mac_tag
            self._cipher = self._siv_ctr_cipher(self._mac)
            pt = self._cipher.decrypt(ciphertext)
            if self.nonce:
                self._cipherMAC.update(self.nonce)
            if pt:
                self._cipherMAC.update(pt)
        else:
            pt = self.decrypt(ciphertext)
        self.verify(mac_tag)
        return pt
