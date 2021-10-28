# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/members_window_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.platoon.button_find_players_cancel_search_model import ButtonFindPlayersCancelSearchModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.button_switch_ready_model import ButtonSwitchReadyModel
from gui.impl.gen.view_models.views.lobby.platoon.event_difficulty_model import EventDifficultyModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.platoon.window_header_model import WindowHeaderModel
from gui.impl.gen.view_models.windows.window_model import WindowModel

class MembersWindowModel(WindowModel):
    __slots__ = ('onFocusChange', 'onOverViewChange')

    def __init__(self, properties=19, commands=4):
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

    @property
    def eventDifficulty(self):
        return self._getViewModel(7)

    def getSlots(self):
        return self._getArray(8)

    def setSlots(self, value):
        self._setArray(8, value)

    def getIsHorizontal(self):
        return self._getBool(9)

    def setIsHorizontal(self, value):
        self._setBool(9, value)

    def getWindowTooltipHeader(self):
        return self._getString(10)

    def setWindowTooltipHeader(self, value):
        self._setString(10, value)

    def getWindowTooltipBody(self):
        return self._getString(11)

    def setWindowTooltipBody(self, value):
        self._setString(11, value)

    def getIsCommander(self):
        return self._getBool(12)

    def setIsCommander(self, value):
        self._setBool(12, value)

    def getIsEvent(self):
        return self._getBool(13)

    def setIsEvent(self, value):
        self._setBool(13, value)

    def getShouldShowFindPlayersButton(self):
        return self._getBool(14)

    def setShouldShowFindPlayersButton(self, value):
        self._setBool(14, value)

    def getShouldShowInvitePlayersButton(self):
        return self._getBool(15)

    def setShouldShowInvitePlayersButton(self, value):
        self._setBool(15, value)

    def getFooterMessage(self):
        return self._getString(16)

    def setFooterMessage(self, value):
        self._setString(16, value)

    def getIsFooterMessageGrey(self):
        return self._getBool(17)

    def setIsFooterMessageGrey(self, value):
        self._setBool(17, value)

    def getSelectedDifficulty(self):
        return self._getString(18)

    def setSelectedDifficulty(self, value):
        self._setString(18, value)

    def _initialize(self):
        super(MembersWindowModel, self)._initialize()
        self._addViewModelProperty('btnInviteFriends', ButtonModel())
        self._addViewModelProperty('btnSwitchReady', ButtonSwitchReadyModel())
        self._addViewModelProperty('btnFindPlayers', ButtonFindPlayersCancelSearchModel())
        self._addViewModelProperty('header', WindowHeaderModel())
        self._addViewModelProperty('eventDifficulty', EventDifficultyModel())
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('isHorizontal', False)
        self._addStringProperty('windowTooltipHeader', '')
        self._addStringProperty('windowTooltipBody', '')
        self._addBoolProperty('isCommander', False)
        self._addBoolProperty('isEvent', False)
        self._addBoolProperty('shouldShowFindPlayersButton', True)
        self._addBoolProperty('shouldShowInvitePlayersButton', True)
        self._addStringProperty('footerMessage', '')
        self._addBoolProperty('isFooterMessageGrey', False)
        self._addStringProperty('selectedDifficulty', '')
        self.onFocusChange = self._addCommand('onFocusChange')
        self.onOverViewChange = self._addCommand('onOverViewChange')
