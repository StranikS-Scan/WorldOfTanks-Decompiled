# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/resources_intro.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, ViewModel
from gui.impl.gen import R
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from new_year.ny_constants import AdditionalCameraObject
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates

class ResourcesIntro(ViewImpl):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.ResourcesIntro())
        settings.model = ViewModel()
        super(ResourcesIntro, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return NyResourceTooltip(event.getArgument('type')) if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip() else super(ResourcesIntro, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(ResourcesIntro, self)._initialize()
        NewYearNavigation.switchTo(AdditionalCameraObject.RESOURCES, withFade=True, instantly=True)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.TUTORIAL_STATE: TutorialStates.FINISHED})


class ResourcesIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self):
        super(ResourcesIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ResourcesIntro(), layer=WindowLayer.OVERLAY)
