# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/comp7_light_prb_helpers.py
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from comp7_light.gui.comp7_light_constants import COMP7_HANGAR_ALIAS, PREBATTLE_ACTION_NAME
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_gui_helper import isComp7LightIntroShouldBeShown
from comp7_light.gui.prb_control.entities.base.ctx import Comp7LightPrbAction
from comp7_light.gui.shared import event_dispatcher as comp7_light_events
from frameworks.wulf import WindowLayer
from gui.app_loader import sf_lobby
from gui.prb_control.entities.base.ctx import PrbAction
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7LightController

@adisp.adisp_process
@dependency.replace_none_kwargs(comp7LightController=IComp7LightController)
def selectComp7Light(comp7LightController=None):
    from gui.prb_control.dispatcher import g_prbLoader
    if not comp7LightController.isEnabled():
        return
    else:
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None:
            yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.COMP7_LIGHT))
        return


@adisp.adisp_process
def createComp7LightSquad(squadSize):
    from gui.prb_control.dispatcher import g_prbLoader
    prbDispatcher = g_prbLoader.getDispatcher()
    if prbDispatcher is not None:
        yield prbDispatcher.doSelectAction(Comp7LightPrbAction(PREBATTLE_ACTION_NAME.COMP7_LIGHT_SQUAD, squadSize=squadSize))
    return


class Comp7LightViewPresenter(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7LightCtrl = dependency.descriptor(IComp7LightController)

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
        if isComp7LightIntroShouldBeShown():
            comp7_light_events.showComp7LightIntroScreen()

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
