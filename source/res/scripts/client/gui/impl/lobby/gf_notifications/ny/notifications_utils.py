# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/notifications_utils.py
from helpers import dependency
from new_year.ny_navigation_helper import switchNewYearView
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from new_year.ny_constants import NYObjects
from gui.shared.event_dispatcher import showStylePreview, hideVehiclePreview, showHangar
from new_year.ny_preview import getVehiclePreviewID

@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def createNavigationAction(objectName, viewAlias, executeBeforeSwitch=None, settingsCore=None):
    if settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE, TutorialStates.INTRO) < TutorialStates.FINISHED:

        def showTutorial():
            switchNewYearView(NYObjects.TOWN, ViewAliases.GLADE_VIEW, instantly=True)

        return showTutorial
    elif objectName is None and NewYearNavigation.getCurrentObject() is not None:

        def switchToView():
            NewYearNavigation.switchToView(viewAlias)

        return switchToView
    else:

        def switchTo():
            toObject = NYObjects.TOWN if objectName is None else objectName
            switchNewYearView(toObject, viewAlias, instantly=True, executeBeforeSwitch=executeBeforeSwitch)
            return

        return switchTo
        return


def createStylePreviewAction(style):

    def showPreview():
        hideVehiclePreview(back=False)
        showStylePreview(getVehiclePreviewID(style), style, descr=style.getDescription(), backCallback=showHangar)

    return showPreview
