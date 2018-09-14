# Embedded file name: scripts/common/Lib/Crypto/Cipher/AES.py
"""AES symmetric cipher

AES `(Advanced Encryption Standard)`__ is a symmetric block cipher standardized
by NIST_ . It has a fixed data block size of 16 bytes.
Its keys can be 128, 192, or 256 bits long.

AES is very fast and secure, and it is the de facto standard for symmetric
encryption.

As an example, encryption can be done as follows:

    >>> from Crypto.Cipher import AES
    >>> from Crypto.Random import get_random_bytes
    >>>
    >>> key = b'Sixteen byte key'
    >>> iv = get_random_bytes(16)
    >>> cipher = AES.new(key, AES.MODE_CFB, iv)
    >>> msg = iv + cipher.encrypt(b'Attack at dawn')

A more complicated example is based on CCM, (see `MODE_CCM`) an `AEAD`_ mode
that provides both confidentiality and authentication for a message.

It optionally allows the header of the message to remain in the clear, whilst still
being authenticated. The encryption is done as follows:

    >>> from Crypto.Cipher import AES
    >>> from Crypto.Random import get_random_bytes
    >>>
    >>>
    >>> hdr = b'To your eyes only'
    >>> plaintext = b'Attack at dawn'
    >>> key = b'Sixteen byte key'
    >>> nonce = get_random_bytes(11)
    >>> cipher = AES.new(key, AES.MODE_CCM, nonce)
    >>> cipher.update(hdr)
    >>> msg = nonce, hdr, cipher.encrypt(plaintext), cipher.digest()

We assume that the tuple ``msg`` is transmitted to the receiver:

    >>> nonce, hdr, ciphertext, mac = msg
    >>> key = b'Sixteen byte key'
    >>> cipher = AES.new(key, AES.MODE_CCM, nonce)
    >>> cipher.update(hdr)
    >>> plaintext = cipher.decrypt(ciphertext)
    >>> try:
    >>>     cipher.verify(mac)
    >>>     print "The message is authentic: hdr=%s, pt=%s" % (hdr, plaintext)
    >>> except ValueError:
    >>>     print "Key incorrect or message corrupted"

.. __: http://en.wikipedia.org/wiki/Advanced_Encryption_Standard
.. _NIST: http://csrc.nist.gov/publications/fips/fips197/fips-197.pdf
.. _AEAD: http://blog.cryptographyengineering.com/2012/05/how-to-choose-authenticated-encryption.html

:undocumented: __revision__, __package__
"""
__revision__ = '$Id$'
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Cipher import blockalgo
import _AES
from Crypto.Util import cpuid
try:
    if cpuid.have_aes_ni():
        from Crypto.Cipher import _AESNI
    else:
        _AESNI = None
except ImportError:
    _AESNI = None

class AESCipher(blockalgo.BlockAlgo):
    """AES cipher object"""

    def __init__(self, key, *args, **kwargs):
        """Initialize an AES cipher object
        
        See also `new()` at the module level."""
        use_aesni = True
        if kwargs.has_key('use_aesni'):
            use_aesni = kwargs['use_aesni']
            del kwargs['use_aesni']
        if _AESNI is not None and use_aesni:
            blockalgo.BlockAlgo.__init__(self, _AESNI, key, *args, **kwargs)
        else:
            blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)
        return


def new(key, *args, **kwargs):
    """Create a new AES cipher
    
    :Parameters:
      key : byte string
        The secret key to use in the symmetric cipher.
        It must be 16 (*AES-128*), 24 (*AES-192*), or 32 (*AES-256*) bytes long.
    
        Only in `MODE_SIV`, it needs to be 32, 48, or 64 bytes long.
    :Keywords:
      mode : a *MODE_** constant
        The chaining mode to use for encryption or decryption.
        Default is `MODE_ECB`.
      IV : byte string
        (*Only* `MODE_CBC`, `MODE_CFB`, `MODE_OFB`, `MODE_OPENPGP`).
    
        The initialization vector to use for encryption or decryption.
    
        It is ignored for `MODE_ECB` and `MODE_CTR`.
    
        For `MODE_OPENPGP`, IV must be `block_size` bytes long for encryption
        and `block_size` +2 bytes for decryption (in the latter case, it is
        actually the *encrypted* IV which was prefixed to the ciphertext).
        It is mandatory.
    
        For all other modes, it must be 16 bytes long.
      nonce : byte string
        (*Only* `MODE_CCM`, `MODE_EAX`, `MODE_GCM`, `MODE_SIV`).
    
        A mandatory value that must never be reused for any other encryption.
    
        For `MODE_CCM`, its length must be in the range ``[7..13]``.
        11 or 12 bytes are reasonable values in general. Bear in
        mind that with CCM there is a trade-off between nonce length and
        maximum message size.
    
        For the other modes, there are no restrictions on its length,
        but it is recommended to use at least 16 bytes.
      counter : callable
        (*Only* `MODE_CTR`). A stateful function that returns the next
        *counter block*, which is a byte string of `block_size` bytes.
        For better performance, use `Crypto.Util.Counter`.
      segment_size : integer
        (*Only* `MODE_CFB`).The number of bits the plaintext and ciphertext
        are segmented in.
        It must be a multiple of 8. If 0 or not specified, it will be assumed to be 8.
      mac_len : integer
        (*Only* `MODE_CCM`). Length of the MAC, in bytes. It must be even and in
        the range ``[4..16]``. The default is 16.
    
        (*Only* `MODE_EAX` and `MODE_GCM`). Length of the MAC, in bytes. It must be no
        larger than 16 bytes (which is the default).
      msg_len : integer
        (*Only* `MODE_CCM`). Length of the message to (de)cipher.
        If not specified, ``encrypt`` or ``decrypt`` may only be called once.
      assoc_len : integer
        (*Only* `MODE_CCM`). Length of the associated data.
        If not specified, all data is internally buffered.
      use_aesni : boolean
        Use AES-NI if available.
    
    :Return: an `AESCipher` object
    """
    return AESCipher(key, *args, **kwargs)


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
block_size = 16
key_size = (16, 24, 32)
