# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/members_window_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.button_switch_ready_model import ButtonSwitchReadyModel
from gui.impl.gen.view_models.views.lobby.platoon.custom_sound_button_model import CustomSoundButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.platoon.window_header_model import WindowHeaderModel
from gui.impl.gen.view_models.windows.window_model import WindowModel

class MembersWindowModel(WindowModel):
    __slots__ = ('onFocusChange',)

    def __init__(self, properties=15, commands=3):
        super(MembersWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def btnInviteFriends(self):
        return self._getViewModel(3)

    @property
    def btnSwitchReady(self):
        return self._getViewModel(4)

    @property
    def btnFindPlayers(self):
        return self._getViewModel(5)

    @property
    def header(self):
        return self._getViewModel(6)

    def getSlots(self):
        return self._getArray(7)

    def setSlots(self, value):
        self._setArray(7, value)

    def getIsHorizontal(self):
        return self._getBool(8)

    def setIsHorizontal(self, value):
        self._setBool(8, value)

    def getWindowTooltipHeader(self):
        return self._getString(9)

    def setWindowTooltipHeader(self, value):
        self._setString(9, value)

    def getWindowTooltipBody(self):
        return self._getString(10)

    def setWindowTooltipBody(self, value):
        self._setString(10, value)

    def getIsCommander(self):
        return self._getBool(11)

    def setIsCommander(self, value):
        self._setBool(11, value)

    def getShouldShowFindPlayersButton(self):
        return self._getBool(12)

    def setShouldShowFindPlayersButton(self, value):
        self._setBool(12, value)

    def getFooterMessage(self):
        return self._getString(13)

    def setFooterMessage(self, value):
        self._setString(13, value)

    def getIsFooterMessageGrey(self):
        return self._getBool(14)

    def setIsFooterMessageGrey(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(MembersWindowModel, self)._initialize()
        self._addViewModelProperty('btnInviteFriends', ButtonModel())
        self._addViewModelProperty('btnSwitchReady', ButtonSwitchReadyModel())
        self._addViewModelProperty('btnFindPlayers', CustomSoundButtonModel())
        self._addViewModelProperty('header', WindowHeaderModel())
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('isHorizontal', False)
        self._addStringProperty('windowTooltipHeader', '')
        self._addStringProperty('windowTooltipBody', '')
        self._addBoolProperty('isCommander', False)
        self._addBoolProperty('shouldShowFindPlayersButton', True)
        self._addStringProperty('footerMessage', '')
        self._addBoolProperty('isFooterMessageGrey', False)
        self.onFocusChange = self._addCommand('onFocusChange')
