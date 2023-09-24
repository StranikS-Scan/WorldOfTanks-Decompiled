# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/comp7/comp7_prb_helpers.py
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from comp7_common import seasonPointsCodeBySeasonNumber
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import sf_lobby
from gui.prb_control.entities.base.ctx import Comp7PrbAction, PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller

@adisp.adisp_process
@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def selectComp7(comp7Controller=None):
    from gui.prb_control.dispatcher import g_prbLoader
    if not comp7Controller.isEnabled():
        return
    else:
        season = comp7Controller.getCurrentSeason()
        prevSeason = comp7Controller.getPreviousSeason()
        if season is not None or prevSeason is not None:
            prbDispatcher = g_prbLoader.getDispatcher()
            if prbDispatcher is not None:
                yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.COMP7))
        else:
            event_dispatcher.showComp7IntroScreen()
        return


@adisp.adisp_process
def createComp7Squad(squadSize):
    from gui.prb_control.dispatcher import g_prbLoader
    prbDispatcher = g_prbLoader.getDispatcher()
    if prbDispatcher is not None:
        yield prbDispatcher.doSelectAction(Comp7PrbAction(PREBATTLE_ACTION_NAME.COMP7_SQUAD, squadSize=squadSize))
    return


class Comp7ViewPresenter(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    @sf_lobby
    def __app(self):
        pass

    def init(self):
        self.__addListeners()
        if self.__isHangarViewLoaded():
            self.__showView()
        else:
            self.__subscribe()

    def fini(self):
        self.__unsubscribe()
        self.__removeListeners()

    def __addListeners(self):
        self.__comp7Ctrl.onSeasonPointsUpdated += self.__onSeasonPointsUpdated

    def __subscribe(self):
        self.__app.loaderManager.onViewLoaded += self.__onViewLoaded

    def __unsubscribe(self):
        self.__app.loaderManager.onViewLoaded -= self.__onViewLoaded

    def __removeListeners(self):
        self.__comp7Ctrl.onSeasonPointsUpdated -= self.__onSeasonPointsUpdated

    def __onViewLoaded(self, view, *_, **__):
        self.__unsubscribe()
        if view.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.__showView()

    def __onSeasonPointsUpdated(self):
        if not self.__isComp7SeasonStasticsShouldBeShown():
            return
        self.__showSeasonStatistic()

    def __showView(self):
        if self.__isComp7OnboardingShouldBeShown():
            self.__showOnboarding()
        elif self.__isComp7WhatsNewShouldBeShown():
            self.__showWhatsNew()
        elif self.__isComp7SeasonStasticsShouldBeShown():
            self.__showSeasonStatistic()

    @classmethod
    def __isHangarViewLoaded(cls):
        container = cls.__app.containerManager.getContainer(WindowLayer.SUB_VIEW)
        if container is not None:
            view = container.getView()
            if hasattr(view, 'alias'):
                return view.alias == VIEW_ALIAS.LOBBY_HANGAR
        return False

    def __isComp7OnboardingShouldBeShown(self):
        return not self.__isViewShown(GuiSettingsBehavior.COMP7_INTRO_SHOWN)

    def __isComp7WhatsNewShouldBeShown(self):
        return not self.__isViewShown(GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN)

    def __isComp7SeasonStasticsShouldBeShown(self):
        currentSeason = self.__comp7Ctrl.getCurrentSeason()
        if currentSeason:
            return False
        previousSeason = self.__comp7Ctrl.getPreviousSeason()
        if not previousSeason:
            return False
        if self.__isViewShown(GuiSettingsBehavior.COMP7_SEASON_STATISTICS_SHOWN):
            return False
        seasonPointsCode = seasonPointsCodeBySeasonNumber(previousSeason.getNumber())
        receivedSeasonPoints = self.__comp7Ctrl.getReceivedSeasonPoints().get(seasonPointsCode)
        return False if not receivedSeasonPoints else True

    @classmethod
    def __isViewShown(cls, key):
        section = cls.__settingsCore.serverSettings.getSection(section=GUI_START_BEHAVIOR, defaults=AccountSettings.getFilterDefault(GUI_START_BEHAVIOR))
        return section.get(key)

    @staticmethod
    def __showOnboarding():
        event_dispatcher.showComp7IntroScreen()

    @staticmethod
    def __showWhatsNew():
        event_dispatcher.showComp7WhatsNewScreen()

    @staticmethod
    def __showSeasonStatistic():
        event_dispatcher.showComp7SeasonStatisticsScreen()
