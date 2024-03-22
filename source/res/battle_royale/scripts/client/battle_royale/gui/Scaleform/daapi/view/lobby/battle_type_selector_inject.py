# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/battle_type_selector_inject.py
from battle_royale.gui.impl.lobby.views.battle_type_selector_view import BattleTypeSelectorView
from gui.Scaleform.daapi.view.meta.BattleTypeSelectorMeta import BattleTypeSelectorMeta
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext

class BattleTypeSelectorInject(BattleTypeSelectorMeta, IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def onPrbEntitySwitched(self):
        self.__update()

    def startFirstShowAnimation(self):
        self.__view.playAnimation(True)

    def startIdleAnimation(self):
        self.__view.playAnimation(False)

    def _makeInjectView(self):
        self.__view = BattleTypeSelectorView()
        return self.__view

    def _populate(self):
        super(BattleTypeSelectorInject, self)._populate()
        self.startGlobalListening()
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__update
        self.__update()

    def _dispose(self):
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__update
        self.stopGlobalListening()
        super(BattleTypeSelectorInject, self)._dispose()

    def __update(self, *_):
        self.setIsVisibleS(self.__battleRoyaleController.isBattleRoyaleMode() and self.__battleRoyaleController.isGeneralHangarEntryPoint() and self.__battleRoyaleController.isInPrimeTime())
