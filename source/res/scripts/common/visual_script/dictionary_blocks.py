# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/dictionary_blocks.py
import base64
import cPickle
import weakref
from visual_script.block import Block, InitParam, EDITOR_TYPE, buildStrKeysValue, Meta
from visual_script.misc import ASPECT, errorVScript
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.type import VScriptType
from debug_utils import LOG_ERROR
from Math import Vector2, Vector3, Vector4, Matrix

class DictionaryMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class Dictionary(VScriptType, dict):

    def __init__(self, storage=None):
        super(Dictionary, self).__init__()
        if storage:
            self.update(storage)

    @classmethod
    def vs_toString(cls, value):
        if value:
            return base64.b64encode(cPickle.dumps(value, -1))
        else:
            return ''

    @classmethod
    def vs_fromString(cls, str_):
        try:
            if str_:
                return cPickle.loads(base64.b64decode(str_))
        except Exception as e:
            LOG_ERROR('[VScript]', 'Error of load Dictionary from string: %s' % e.message)

        return Dictionary()

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]

    @classmethod
    def vs_connectionColor(cls):
        pass


ALLOWED_DATA_TYPES = {'String': (str,),
 'Bool': (bool,),
 'Int': (int, long),
 'Float': (float,),
 'Vehicle': (weakref.ProxyType,),
 'Dictionary': (dict, Dictionary),
 'Vector2': (Vector2,),
 'Vector3': (Vector3,),
 'Vector4': (Vector4,),
 'Matrix4': (Matrix,)}

class EmptyDictionary(Block, DictionaryMeta):

    def __init__(self, *args, **kwargs):
        super(EmptyDictionary, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.DICTIONARY, self._get)

    def _get(self):
        return Dictionary()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class AddToDictionary(Block, DictionaryMeta):

    def __init__(self, *args, **kwargs):
        super(AddToDictionary, self).__init__(*args, **kwargs)
        self._valueType, self._isArray = self._getInitParams()
        if self._isArray:
            self._valueType = arrayOf(self._valueType)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._dict = self._makeDataInputSlot('dict', SLOT_TYPE.DICTIONARY)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._value = self._makeDataInputSlot('value', self._valueType)
        self._override = self._makeDataInputSlot('override', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.DICTIONARY, None)
        return

    def _exec(self):
        res = Dictionary(self._dict.getValue())
        key = self._key.getValue()
        value = self._value.getValue()
        override = self._override.getValue()
        if override or key not in res:
            res[key] = value
        self._res.setValue(res)
        self._out.call()

    @classmethod
    def initParams(cls):
        return [InitParam('Value type', SLOT_TYPE.STR, buildStrKeysValue(*ALLOWED_DATA_TYPES.iterkeys()), EDITOR_TYPE.STR_KEY_SELECTOR), InitParam('Is Array', SLOT_TYPE.BOOL, False)]

    def captionText(self):
        return 'Add To Dictionary: {}'.format(self._valueType)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class IsInDictionary(Block, DictionaryMeta):

    def __init__(self, *args, **kwargs):
        super(IsInDictionary, self).__init__(*args, **kwargs)
        self._valueType = self._getInitParams()
        self._dict = self._makeDataInputSlot('dict', SLOT_TYPE.DICTIONARY)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._checkKey)

    def _checkKey(self):
        keyValueStorage = self._dict.getValue()
        key = self._key.getValue()
        if key in keyValueStorage:
            valueType = type(keyValueStorage[key])
            if valueType in ALLOWED_DATA_TYPES[self._valueType]:
                self._res.setValue(True)
                return
        self._res.setValue(False)

    @classmethod
    def initParams(cls):
        return [InitParam('Value type', SLOT_TYPE.STR, buildStrKeysValue(*ALLOWED_DATA_TYPES.iterkeys()), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def captionText(self):
        return 'Is In Dictionary: {}'.format(self._valueType)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class GetFromDictionary(Block, DictionaryMeta):

    def __init__(self, *args, **kwargs):
        super(GetFromDictionary, self).__init__(*args, **kwargs)
        self._valueType, self._isArray = self._getInitParams()
        self._dict = self._makeDataInputSlot('dict', SLOT_TYPE.DICTIONARY)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._value = self._makeDataOutputSlot('value', arrayOf(self._valueType), self._getArrayValue) if self._isArray else self._makeDataOutputSlot('value', self._valueType, self._getValue)

    def _getArrayValue(self):
        keyValueStorage = self._dict.getValue()
        key = self._key.getValue()
        if key not in keyValueStorage:
            errorVScript(self, 'Key {} is missing in the Dictionary'.format(key))
            return
        value = keyValueStorage[key]
        valueType = type(value)
        if valueType not in (list, tuple):
            errorVScript(self, 'Value type mismatch for key {} in the Dictionary.Expected {}, received {}'.format(key, 'list or tuple', valueType))
            return
        if value and type(value[0]) not in ALLOWED_DATA_TYPES[self._valueType]:
            errorVScript(self, 'List value type mismatch for key {} in the Dictionary.Expected {}, received {}'.format(key, self._valueType, type(value[0])))
            return
        if valueType is dict:
            self._value.setValue([ Dictionary(val) for val in value ])
        else:
            self._value.setValue(value)

    def _getValue(self):
        keyValueStorage = self._dict.getValue()
        key = self._key.getValue()
        if key in keyValueStorage:
            value = keyValueStorage[key]
            valueType = type(value)
            if valueType in ALLOWED_DATA_TYPES[self._valueType]:
                if valueType is dict:
                    self._value.setValue(Dictionary(value))
                else:
                    self._value.setValue(value)
            else:
                errorVScript(self, 'Value type mismatch for key {} in the Dictionary. Expected {}, received {}'.format(key, self._valueType, valueType))
        else:
            errorVScript(self, 'Key {} is missing in the Dictionary'.format(key))

    @classmethod
    def initParams(cls):
        return [InitParam('Value type', SLOT_TYPE.STR, buildStrKeysValue(*ALLOWED_DATA_TYPES.iterkeys()), EDITOR_TYPE.STR_KEY_SELECTOR), InitParam('Is Array', SLOT_TYPE.BOOL, False)]

    def captionText(self):
        return 'Get From Dictionary: {}'.format(arrayOf(self._valueType) if self._isArray else self._valueType)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]
