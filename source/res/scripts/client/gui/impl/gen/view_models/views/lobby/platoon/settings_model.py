# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/settings_model.py
import typing
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.tiers_settings_model import TiersSettingsModel
from gui.impl.gen.view_models.views.lobby.platoon.voice_chat_settings_model import VoiceChatSettingsModel
F = typing.TypeVar('F')

class SearchFilterTypes(Enum):
    VOICE = 'voice'
    TIER = 'tier'


class SettingsModel(ViewModel, typing.Generic[F]):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SettingsModel, self).__init__(properties=properties, commands=commands)

    @property
    def tiersSettings(self):
        return self._getViewModel(0)

    @property
    def voiceSettings(self):
        return self._getViewModel(1)

    def getSearchFilterTypes(self):
        return self._getArray(2)

    def setSearchFilterTypes(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(SettingsModel, self)._initialize()
        self._addViewModelProperty('tiersSettings', TiersSettingsModel())
        self._addViewModelProperty('voiceSettings', VoiceChatSettingsModel())
        self._addArrayProperty('searchFilterTypes', Array())
