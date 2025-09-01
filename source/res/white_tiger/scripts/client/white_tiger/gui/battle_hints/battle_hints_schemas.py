# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_hints/battle_hints_schemas.py
from hints.battle.schemas.base import ClientHintModel, ClientHintSchema, CHMTextType, HMCContextType, CHMVisualType, CHMLifecycleType, HMCPropsType, CHMSoundType, CHMHistoryType

class WhiteTigerClientHintModel(ClientHintModel[HMCPropsType, HMCContextType, CHMTextType, CHMVisualType, CHMSoundType, CHMLifecycleType, CHMHistoryType]):
    __slots__ = ()

    def _createVO(self, data):
        vo = super(WhiteTigerClientHintModel, self)._createVO(data)
        timer = self.lifecycle.showTime * 1000 if self.lifecycle else 0
        vo['timer'] = timer
        return vo


hintSchema = ClientHintSchema[WhiteTigerClientHintModel](modelClass=WhiteTigerClientHintModel)
