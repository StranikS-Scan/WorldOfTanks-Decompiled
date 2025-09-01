# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/entities/comp7_prb_helpers.py
import logging
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME, COMP7_HANGAR_ALIAS
from comp7.gui.impl.lobby.comp7_helpers.comp7_gui_helpers import isComp7OnboardingShouldBeShown, isComp7WhatsNewShouldBeShown
from comp7.gui.prb_control.entities.base.ctx import Comp7PrbAction
from comp7.gui.shared import event_dispatcher as comp7_events
from frameworks.wulf import WindowLayer
from gui.app_loader import sf_lobby
from gui.prb_control.entities.base.ctx import PrbAction
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)

@adisp.adisp_process
@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def selectComp7(comp7Controller=None):
    from gui.prb_control.dispatcher import g_prbLoader
    if not comp7Controller.isEnabled():
        return
    else:
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None:
            yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.COMP7))
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
        if self.__isHangarViewLoaded():
            self.__showView()
        else:
            self.__subscribe()

    def fini(self):
        self.__unsubscribe()

    def __subscribe(self):
        self.__app.loaderManager.onViewLoaded += self.__onViewLoaded

    def __unsubscribe(self):
        self.__app.loaderManager.onViewLoaded -= self.__onViewLoaded

    def __onViewLoaded(self, view, *_, **__):
        self.__unsubscribe()
        if view.alias == COMP7_HANGAR_ALIAS:
            self.__showView()

    def __showView(self):
        if isComp7OnboardingShouldBeShown():
            self.__showOnboarding()
        elif isComp7WhatsNewShouldBeShown():
            self.__showWhatsNew()

    @classmethod
    def __isHangarViewLoaded(cls):
        container = cls.__app.containerManager.getContainer(WindowLayer.SUB_VIEW)
        if container is not None:
            view = container.getView()
            if hasattr(view, 'alias'):
                return view.alias == COMP7_HANGAR_ALIAS
        return False

    @classmethod
    def __isViewShown(cls, key):
        section = cls.__settingsCore.serverSettings.getSection(section=GUI_START_BEHAVIOR, defaults=AccountSettings.getFilterDefault(GUI_START_BEHAVIOR))
        return section.get(key)

    @staticmethod
    def __showOnboarding():
        comp7_events.showComp7IntroScreen()

    @staticmethod
    def __showWhatsNew():
        comp7_events.showComp7WhatsNewScreen()
