# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/players_panel.py
from weakref import proxy
from gui.Scaleform.windows import UIInterface
from gui.battle_control.arena_info import isEventBattle

class _EmptyPlayersPanel(UIInterface):

    def defineColorFlags(self, isColorBlind = False):
        pass

    def getPlayerNameLength(self):
        return 31


class _GeneralPlayersPanel(_EmptyPlayersPanel):

    def __init__(self, parentUI, isLeft, isColorBlind = False):
        super(_GeneralPlayersPanel, self).__init__()
        self.proxy = proxy(self)
        self.GUICtrl = None
        self.__parentUI = parentUI
        self.__isLeft = isLeft
        self.__colorGroup = None
        self.defineColorFlags(isColorBlind=isColorBlind)
        return

    def populateUI(self, proxy):
        super(_GeneralPlayersPanel, self).populateUI(proxy)
        if self.__isLeft:
            self.GUICtrl = self.uiHolder.getMember('_level0.leftPanel')
        else:
            self.GUICtrl = self.uiHolder.getMember('_level0.rightPanel')
        self.GUICtrl.script = self

    def dispossessUI(self):
        if self.GUICtrl:
            self.GUICtrl.script = None
            self.GUICtrl = None
        super(_GeneralPlayersPanel, self).dispossessUI()
        return

    def defineColorFlags(self, isColorBlind = False):
        self.__colorGroup = 'color_blind' if isColorBlind else 'default'

    def getPlayerNameLength(self):
        return self.GUICtrl.getPlayerNameLength()


def playersPanelFactory(parentUI, isLeft, isColorBlind = False):
    if isEventBattle():
        return _EmptyPlayersPanel()
    return _GeneralPlayersPanel(parentUI, isLeft, isColorBlind)
