# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/views/quests_tab_view.py
from frontline.gui.impl.gen.view_models.views.battle.quests_tab_model import QuestsTabModel
from frontline.views.quests_view import EpicBattleQuestsView
from frontline.gui.Scaleform.daapi.view.battle.sector_progression import SectorProgressionCmpView
from PlayerEvents import g_playerEvents
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleController
from frameworks.wulf import ViewSettings, ViewFlags

class EpicBattleQuestsTabView(EpicBattleQuestsView):
    __battleController = dependency.descriptor(IEpicBattleController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(R.views.frontline.battle.QuestsTabView())
        settings.flags = ViewFlags.VIEW
        settings.model = QuestsTabModel()
        self.__isClientReady = False
        super(EpicBattleQuestsTabView, self).__init__(settings)

    @classmethod
    def _playSoundNotification(cls, sound):
        pass

    def _playSound(self, sound):
        pass

    def _getEvents(self):
        events = ((self.__battleController.onProgressionModelChanged, self.__onProgressionModelChanged), (g_playerEvents.onArenaStateChange, self.__onArenaStateChange))
        events += super(EpicBattleQuestsTabView, self)._getEvents()
        return events

    def __onArenaStateChange(self, isClientReady, _):
        self.__isClientReady = isClientReady

    def __onProgressionModelChanged(self, _, progression):
        with self.viewModel.transaction() as vm:
            SectorProgressionCmpView.fillProgressionArrayModels(progression, vm.getProgressions())
            vm.setIsClientReady(self.__isClientReady)
            self.__updateAimSector(vm)

    def __updateAimSector(self, vm):
        sectorID = self.__battleController.getAimSector()
        if sectorID <= 0:
            vm.setSectorName(backport.text(R.strings.fl_quests.quest.line.last()))
            vm.setIsLastLine(True)
            return
        vm.setSectorName(backport.text(R.strings.fl_quests.questTab.zone(), name=self.__battleController.getSectorName(sectorID)))
        vm.setIsLastLine(False)


class EpicBattleQuestTabInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = EpicBattleQuestsTabView()
        return self.__view
