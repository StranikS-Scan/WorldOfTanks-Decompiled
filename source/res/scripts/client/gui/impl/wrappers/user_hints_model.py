# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_hints_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.hint_model import HintModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.hints_model import HintsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from gui.shared.tutorial_helper import getTutorialGlobalStorage

class UserHintsModel(HintsModel):

    def addHintModel(self, hintName):
        hintModel = HintModel()
        hintModel.setName(hintName)
        tutorialGlobalStorage = getTutorialGlobalStorage()
        if tutorialGlobalStorage:
            isHintZoneActive = tutorialGlobalStorage.getValue(hintName)
            if isHintZoneActive is not None:
                hintModel.setIsTargetHidden(not isHintZoneActive)
        self.getHints().addViewModel(hintModel)
        self.getHints().invalidate()
        self.setSyncInitiator((self.getSyncInitiator() + 1) % 1000)
        return

    def getHintModel(self, hintName):
        index = self.__getIndexByHintName(hintName)
        return self.getHints()[index] if index is not None else None

    def delHintModel(self, hintName):
        index = self.__getIndexByHintName(hintName)
        if index is not None:
            self.getHints().remove(index)
        return

    def hasHintModel(self, hintName):
        index = self.__getIndexByHintName(hintName)
        return index is not None

    def _initialize(self):
        super(UserHintsModel, self)._initialize()
        self.onHintZoneAdded += self.__onHintZoneAdded
        self.onHintZoneHidden += self.__onHintZoneHidden
        self.onHintZoneClicked += self.__onHintZoneClicked
        tutorialGlobalStorage = getTutorialGlobalStorage()
        if tutorialGlobalStorage:
            tutorialGlobalStorage.onSetValue += self.__onHintZoneActivated

    def _finalize(self):
        self.onHintZoneAdded -= self.__onHintZoneAdded
        self.onHintZoneHidden -= self.__onHintZoneHidden
        self.onHintZoneClicked -= self.__onHintZoneClicked
        tutorialGlobalStorage = getTutorialGlobalStorage()
        if tutorialGlobalStorage:
            tutorialGlobalStorage.onSetValue -= self.__onHintZoneActivated
        super(UserHintsModel, self)._finalize()

    def __onHintZoneActivated(self, hintZoneName, isActive):
        with self.transaction() as model:
            for hintModel in model.getHints():
                if hintModel.getName() == hintZoneName and isActive is not None:
                    hintModel.setIsTargetHidden(not isActive)

            model.getHints().invalidate()
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)
        return

    def __getIndexByHintName(self, hintName):
        for index, hintModel in enumerate(self.getHints()):
            if hintModel.getName() == hintName:
                return index

        return None

    def __onHintZoneAdded(self, args):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_ADD, ctx=args), EVENT_BUS_SCOPE.LOBBY)

    def __onHintZoneHidden(self, args):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx=args), EVENT_BUS_SCOPE.LOBBY)

    def __onHintZoneClicked(self, args):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_CLICK, ctx=args), EVENT_BUS_SCOPE.LOBBY)
