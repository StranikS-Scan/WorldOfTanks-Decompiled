# Embedded file name: scripts/client/helpers/obfuscators.py
import base64
from debug_utils import LOG_CURRENT_EXCEPTION

class XORObfuscator:
    __PREFIX = '#obfuscate:'

    def __init__(self, key):
        if len(key) < 1:
            raise ValueError, 'Key length must be at least one character'
        self.__key = key

    def __doXor(self, data):
        kIdx = 0
        processed = []
        for x in range(len(data)):
            processed.append(chr(ord(data[x]) ^ ord(self.__key[kIdx])))
            kIdx = (kIdx + 1) % len(self.__key)

        return ''.join(processed)

    def obfuscate(self, data):
        return base64.b64encode(self.__PREFIX + self.__doXor(data))

    def unobfuscate(self, data):
        if len(data.strip()) % 4 != 0:
            return data
        try:
            decode = base64.b64decode(data)
        except:
            LOG_CURRENT_EXCEPTION()
            return data

        if decode.startswith(self.__PREFIX):
            return self.__doXor(decode[len(self.__PREFIX):])
        return data


class PasswordObfuscator(XORObfuscator):

    def __init__(self):
        XORObfuscator.__init__(self, '416c34666745786b'.decode('hex'))
