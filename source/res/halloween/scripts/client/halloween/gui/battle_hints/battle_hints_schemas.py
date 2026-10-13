# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_hints/battle_hints_schemas.py
from __future__ import absolute_import
from dict2model import fields
from dict2model import schemas
from dict2model import validate
from hints_common.battle.schemas.base import CommonHintContextModel
from hints.battle.schemas.base import validateHintTextTemplate, ClientHintModel, ClientHintSchema, ClientHintTextModel, ClientHintTextSchema, CHMVisualType, CHMLifecycleType, HMCPropsType, CHMSoundType, CHMHistoryType

class HalloweenHintContextModel(CommonHintContextModel):
    __slots__ = ('extraPadding', 'offsetY', 'isAdaptive')

    def __init__(self, extraPadding, offsetY, isAdaptive):
        super(HalloweenHintContextModel, self).__init__()
        self.extraPadding = extraPadding
        self.offsetY = offsetY
        self.isAdaptive = isAdaptive


hintContextSchema = schemas.Schema[HalloweenHintContextModel](fields={'extraPadding': fields.Integer(default=0, required=False),
 'offsetY': fields.Integer(default=0, required=False),
 'isAdaptive': fields.Boolean(default=False, required=False)}, checkUnknown=True, modelClass=HalloweenHintContextModel)

class HalloweenHintTextModel(ClientHintTextModel):
    __slots__ = ('templatePinnable', '_messagePinnable')

    def __init__(self, raw, key, template, highlight, templatePinnable):
        super(HalloweenHintTextModel, self).__init__(raw=raw, key=key, template=template, highlight=highlight)
        self.templatePinnable = templatePinnable
        self._messagePinnable = self._createMessage(template=self.templatePinnable)

    @property
    def messagePinnable(self):
        return self._messagePinnable

    def _reprArgs(self):
        return '{}, {}'.format(super(HalloweenHintTextModel, self)._reprArgs(), 'templatePinnable={}, messagePinnable={}'.format(self.templatePinnable, self._messagePinnable))


class HalloweenHintTextSchema(ClientHintTextSchema[HalloweenHintTextModel]):
    __slots__ = ()

    def __init__(self):
        super(HalloweenHintTextSchema, self).__init__(checkUnknown=True, modelClass=HalloweenHintTextModel)
        self._fields['templatePinnable'] = fields.String(required=False, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100), validateHintTextTemplate])


class HalloweenHintModel(ClientHintModel[HMCPropsType, HalloweenHintContextModel, HalloweenHintTextModel, CHMVisualType, CHMSoundType, CHMLifecycleType, CHMHistoryType]):
    __slots__ = ()

    def _createVO(self, data):
        vo = super(HalloweenHintModel, self)._createVO(data)
        if self.text and self.text.messagePinnable:
            vo['messagePinnable'] = self.text.messagePinnable
        return vo


hintTextSchema = HalloweenHintTextSchema()
hintSchema = ClientHintSchema[HalloweenHintModel](textSchema=hintTextSchema, contextSchema=hintContextSchema, modelClass=HalloweenHintModel)
