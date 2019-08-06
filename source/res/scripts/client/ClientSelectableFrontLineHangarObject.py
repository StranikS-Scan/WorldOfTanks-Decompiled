# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableFrontLineHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.game_control.epic_meta_game_ctrl import FRONTLINE_SCREENS
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class ClientSelectableFrontLineHangarObject(ClientSelectableObject):
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def onMouseClick(self):
        super(ClientSelectableFrontLineHangarObject, self).onMouseClick()
        self.__epicCtrl.showCustomScreen(FRONTLINE_SCREENS.FESTIVAL_REWARDS_SCREEN)
