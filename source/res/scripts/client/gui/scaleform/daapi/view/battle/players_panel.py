# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/players_panel.py
from weakref import proxy
from gui.Scaleform.windows import UIInterface

class _EmptyPlayersPanel(UIInterface):

    def defineColorFlags(self, isColorBlind = False):
        pass

    def getPlayerNameLength(self):
        pass

    def getVehicleNameLength(self):
        pass


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

    def populateUI(self, uiProxy):
        super(_GeneralPlayersPanel, self).populateUI(uiProxy)
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

    def getVehicleNameLength(self):
        return self.GUICtrl.getVehicleNameLength()


class _FalloutPlayersPanel(_EmptyPlayersPanel):

    def getPlayerNameLength(self):
        pass

    def getVehicleNameLength(self):
        pass


class _MultiTeamsPlayersPanel(_EmptyPlayersPanel):

    def getPlayerNameLength(self):
        pass

    def getVehicleNameLength(self):
        pass


def playersPanelFactory(parentUI, isLeft, isColorBlind = False, isEvent = False, isMutlipleTeams = False):
    if isEvent:
        if isMutlipleTeams:
            return _MultiTeamsPlayersPanel()
        return _FalloutPlayersPanel()
    return _GeneralPlayersPanel(parentUI, isLeft, isColorBlind)
