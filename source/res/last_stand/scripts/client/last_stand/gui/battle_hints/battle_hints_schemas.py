# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_hints/battle_hints_schemas.py
from __future__ import absolute_import
from dict2model import fields
from dict2model import schemas
from dict2model import validate
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from hints.battle.schemas.const import HTML_TEMPLATE_PATH
from hints_common.battle.schemas.base import CommonHintContextModel
from hints.battle.schemas.base import validateHintTextTemplate, ClientHintModel, ClientHintSchema, ClientHintTextModel, ClientHintTextSchema, CHMVisualType, CHMLifecycleType, HMCPropsType, CHMSoundType, CHMHistoryType

class LSHintContextModel(CommonHintContextModel):
    __slots__ = ('extraPadding', 'offsetY', 'isAdaptive')

    def __init__(self, extraPadding, offsetY, isAdaptive):
        super(LSHintContextModel, self).__init__()
        self.extraPadding = extraPadding
        self.offsetY = offsetY
        self.isAdaptive = isAdaptive


hintContextSchema = schemas.Schema[LSHintContextModel](fields={'extraPadding': fields.Integer(default=0, required=False),
 'offsetY': fields.Integer(default=0, required=False),
 'isAdaptive': fields.Boolean(default=False, required=False)}, checkUnknown=True, modelClass=LSHintContextModel)

class LSHintTextModel(ClientHintTextModel):
    __slots__ = ('templatePinnable', '_templateSmall', '_messagePinnable')

    def __init__(self, raw, key, template, highlight, templatePinnable, templateSmall):
        super(LSHintTextModel, self).__init__(raw=raw, key=key, template=template, highlight=highlight)
        self.templatePinnable = templatePinnable
        self._templateSmall = templateSmall
        self._messagePinnable = self._createMessage(template=self.templatePinnable)

    @property
    def messagePinnable(self):
        return self._messagePinnable

    @property
    def templateSmall(self):
        return self._templateSmall

    def _reprArgs(self):
        return '{}, {}'.format(super(LSHintTextModel, self)._reprArgs(), 'templatePinnable={}, templateSmall={}, messagePinnable={}'.format(self.templatePinnable, self._templateSmall, self._messagePinnable))


class LSHintTextSchema(ClientHintTextSchema[LSHintTextModel]):
    __slots__ = ()

    def __init__(self):
        super(LSHintTextSchema, self).__init__(checkUnknown=True, modelClass=LSHintTextModel)
        self._fields['templatePinnable'] = fields.String(required=False, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100), validateHintTextTemplate])
        self._fields['templateSmall'] = fields.String(required=False, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100), validateHintTextTemplate])


class LSHintModel(ClientHintModel[HMCPropsType, LSHintContextModel, LSHintTextModel, CHMVisualType, CHMSoundType, CHMLifecycleType, CHMHistoryType]):
    __slots__ = ()

    def _createVO(self, data):
        vo = super(LSHintModel, self)._createVO(data)
        name, points = data.get('name', ''), data.get('points', 0)
        if self.text and self.props.name == 'destroyObelisk' and name:
            obeliskName = backport.text(R.strings.last_stand_battle.battleHint.destroyObelisk.title.name.dyn(name)())
            title = backport.text(R.strings.last_stand_battle.battleHint.destroyObelisk.title(), name=obeliskName)
            obeliskBonus = backport.text(R.strings.last_stand_battle.battleHint.destroyObelisk.subtitle.bonus.dyn(name)())
            buffBonus = backport.text(R.strings.last_stand_battle.battleHint.destroyObelisk.subtitle.bonus(), buffBonus=obeliskBonus)
            vo['message'] = makeHtmlString(HTML_TEMPLATE_PATH, self.text.template, ctx={'title': title,
             'points': points,
             'bonus': buffBonus})
            vo['messageSmall'] = makeHtmlString(HTML_TEMPLATE_PATH, self.text.templateSmall, ctx={'title': title,
             'points': points,
             'bonus': buffBonus})
            vo['isGlow'] = True
        if self.text and self.text.messagePinnable:
            vo['messagePinnable'] = self.text.messagePinnable
        return vo


hintTextSchema = LSHintTextSchema()
hintSchema = ClientHintSchema[LSHintModel](textSchema=hintTextSchema, contextSchema=hintContextSchema, modelClass=LSHintModel)
