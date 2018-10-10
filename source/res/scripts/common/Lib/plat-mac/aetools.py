# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/aetools.py
from warnings import warnpy3k
warnpy3k('In 3.x, the aetools module is removed.', stacklevel=2)
from types import *
from Carbon import AE
from Carbon import Evt
from Carbon import AppleEvents
import MacOS
import sys
import time
from aetypes import *
from aepack import packkey, pack, unpack, coerce, AEDescType
Error = 'aetools.Error'
LAUNCH_MAX_WAIT_TIME = 10
aekeywords = ['tran',
 'rtid',
 'evcl',
 'evid',
 'addr',
 'optk',
 'timo',
 'inte',
 'esrc',
 'miss',
 'from']

def missed(ae):
    try:
        desc = ae.AEGetAttributeDesc('miss', 'keyw')
    except AE.Error as msg:
        return None

    return desc.data


def unpackevent(ae, formodulename=''):
    parameters = {}
    try:
        dirobj = ae.AEGetParamDesc('----', '****')
    except AE.Error:
        pass
    else:
        parameters['----'] = unpack(dirobj, formodulename)
        del dirobj

    try:
        dirobj = ae.AEGetParamDesc('errn', '****')
    except AE.Error:
        pass
    else:
        parameters['errn'] = unpack(dirobj, formodulename)
        del dirobj

    while 1:
        key = missed(ae)
        if not key:
            break
        parameters[key] = unpack(ae.AEGetParamDesc(key, '****'), formodulename)

    attributes = {}
    for key in aekeywords:
        try:
            desc = ae.AEGetAttributeDesc(key, '****')
        except (AE.Error, MacOS.Error) as msg:
            if msg[0] != -1701 and msg[0] != -1704:
                raise
            continue

        attributes[key] = unpack(desc, formodulename)

    return (parameters, attributes)


def packevent(ae, parameters={}, attributes={}):
    for key, value in parameters.items():
        packkey(ae, key, value)

    for key, value in attributes.items():
        ae.AEPutAttributeDesc(key, pack(value))


def keysubst(arguments, keydict):
    ok = keydict.values()
    for k in arguments.keys():
        if k in keydict:
            v = arguments[k]
            del arguments[k]
            arguments[keydict[k]] = v
        if k != '----' and k not in ok:
            raise TypeError, 'Unknown keyword argument: %s' % k


def enumsubst(arguments, key, edict):
    if key not in arguments or edict is None:
        return
    else:
        v = arguments[key]
        ok = edict.values()
        if v in edict:
            arguments[key] = Enum(edict[v])
        elif v not in ok:
            raise TypeError, 'Unknown enumerator: %s' % v
        return


def decodeerror(arguments):
    errn = arguments['errn']
    err_a1 = errn
    if 'errs' in arguments:
        err_a2 = arguments['errs']
    else:
        err_a2 = MacOS.GetErrorString(errn)
    if 'erob' in arguments:
        err_a3 = arguments['erob']
    else:
        err_a3 = None
    return (err_a1, err_a2, err_a3)


class TalkTo:
    _signature = None
    _moduleName = None
    _elemdict = {}
    _propdict = {}
    __eventloop_initialized = 0

    def __ensure_WMAvailable(klass):
        if klass.__eventloop_initialized:
            return 1
        if not MacOS.WMAvailable():
            return 0
        Evt.WaitNextEvent(0, 0)

    __ensure_WMAvailable = classmethod(__ensure_WMAvailable)

    def __init__(self, signature=None, start=0, timeout=0):
        self.target_signature = None
        if signature is None:
            signature = self._signature
        if type(signature) == AEDescType:
            self.target = signature
        elif type(signature) == InstanceType and hasattr(signature, '__aepack__'):
            self.target = signature.__aepack__()
        elif type(signature) == StringType and len(signature) == 4:
            self.target = AE.AECreateDesc(AppleEvents.typeApplSignature, signature)
            self.target_signature = signature
        else:
            raise TypeError, 'signature should be 4-char string or AEDesc'
        self.send_flags = AppleEvents.kAEWaitReply
        self.send_priority = AppleEvents.kAENormalPriority
        if timeout:
            self.send_timeout = timeout
        else:
            self.send_timeout = AppleEvents.kAEDefaultTimeout
        if start:
            self._start()
        return

    def _start(self):
        try:
            self.send('ascr', 'noop')
        except AE.Error:
            _launch(self.target_signature)
            for i in range(LAUNCH_MAX_WAIT_TIME):
                try:
                    self.send('ascr', 'noop')
                except AE.Error:
                    pass
                else:
                    break

                time.sleep(1)

    def start(self):
        self._start()

    def newevent(self, code, subcode, parameters={}, attributes={}):
        event = AE.AECreateAppleEvent(code, subcode, self.target, AppleEvents.kAutoGenerateReturnID, AppleEvents.kAnyTransactionID)
        packevent(event, parameters, attributes)
        return event

    def sendevent(self, event):
        if not self.__ensure_WMAvailable():
            raise RuntimeError, 'No window manager access, cannot send AppleEvent'
        reply = event.AESend(self.send_flags, self.send_priority, self.send_timeout)
        parameters, attributes = unpackevent(reply, self._moduleName)
        return (reply, parameters, attributes)

    def send(self, code, subcode, parameters={}, attributes={}):
        return self.sendevent(self.newevent(code, subcode, parameters, attributes))

    def activate(self):
        self.send('misc', 'actv')

    def _get(self, _object, asfile=None, _attributes={}):
        _code = 'core'
        _subcode = 'getd'
        _arguments = {'----': _object}
        if asfile:
            _arguments['rtyp'] = mktype(asfile)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if 'errn' in _arguments:
            raise Error, decodeerror(_arguments)
        if '----' in _arguments:
            return _arguments['----']
            if asfile:
                item.__class__ = asfile
            return item

    get = _get
    _argmap_set = {'to': 'data'}

    def _set(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'setd'
        keysubst(_arguments, self._argmap_set)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise Error, decodeerror(_arguments)
        return _arguments['----'] if '----' in _arguments else None

    set = _set

    def __getattr__(self, name):
        if name in self._elemdict:
            cls = self._elemdict[name]
            return DelayedComponentItem(cls, None)
        elif name in self._propdict:
            cls = self._propdict[name]
            return cls()
        else:
            raise AttributeError, name
            return None


class _miniFinder(TalkTo):

    def open(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'odoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if 'errn' in _arguments:
            raise Error, decodeerror(_arguments)
        return _arguments['----'] if '----' in _arguments else None


_finder = _miniFinder('MACS')

def _launch(appfile):
    _finder.open(_application_file(('ID  ', appfile)))


class _application_file(ComponentItem):
    want = 'appf'


_application_file._propdict = {}
_application_file._elemdict = {}

def test():
    target = AE.AECreateDesc('sign', 'quil')
    ae = AE.AECreateAppleEvent('aevt', 'oapp', target, -1, 0)
    print unpackevent(ae)
    raw_input(':')
    ae = AE.AECreateAppleEvent('core', 'getd', target, -1, 0)
    obj = Character(2, Word(1, Document(1)))
    print obj
    print repr(obj)
    packevent(ae, {'----': obj})
    params, attrs = unpackevent(ae)
    print params['----']
    raw_input(':')


if __name__ == '__main__':
    test()
    sys.exit(1)
