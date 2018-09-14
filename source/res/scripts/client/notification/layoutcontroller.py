# Embedded file name: scripts/client/notification/LayoutController.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from notification.BaseMessagesController import BaseMessagesController
from notification.settings import LAYOUT_PADDING

class LayoutController(BaseMessagesController, EventSystemEntity, AppRef):

    def __init__(self, model):
        BaseMessagesController.__init__(self, model)
        isViewAvailable = self.app.containerManager.isViewAvailable(ViewTypes.LOBBY_SUB)
        if isViewAvailable:
            view = self.app.containerManager.getView(ViewTypes.LOBBY_SUB)
            isNowHangarLoading = view.settings.alias == VIEW_ALIAS.LOBBY_HANGAR
        else:
            isNowHangarLoading = self.app.loaderManager.isViewLoading(VIEW_ALIAS.LOBBY_HANGAR)
        if isNowHangarLoading:
            self.__onHangarViewSelected({})
        else:
            self.__onSomeViewSelected({})
        self.addListener(VIEW_ALIAS.LOBBY_HANGAR, self.__onHangarViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_INVENTORY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_SHOP, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_PROFILE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_TECHTREE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_RESEARCH, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_BARRACKS, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.LOBBY_CUSTOMIZATION, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.BATTLE_QUEUE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.BATTLE_LOADING, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(VIEW_ALIAS.TUTORIAL_LOADING, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)

    def __onSomeViewSelected(self, _):
        self._model.setLayoutSettings(*LAYOUT_PADDING.OTHER)

    def __onHangarViewSelected(self, _):
        self._model.setLayoutSettings(*LAYOUT_PADDING.HANGAR)

    def cleanUp(self):
        self.removeListener(VIEW_ALIAS.LOBBY_HANGAR, self.__onHangarViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_INVENTORY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_SHOP, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_PROFILE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_TECHTREE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_RESEARCH, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_BARRACKS, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.LOBBY_CUSTOMIZATION, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.BATTLE_QUEUE, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.BATTLE_LOADING, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(VIEW_ALIAS.TUTORIAL_LOADING, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, self.__onSomeViewSelected, EVENT_BUS_SCOPE.LOBBY)
        BaseMessagesController.cleanUp(self)
