# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/comp7_light_helpers/comp7_light_gui_helper.py
from account_helpers import AccountSettings
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from account_helpers.AccountSettings import COMP7_LIGHT_UI_SECTION, COMP7_LIGHT_LAST_SEASON

@dependency.replace_none_kwargs(comp7LightController=IComp7LightController)
def isComp7LightIntroShouldBeShown(comp7LightController=None):
    if not comp7LightController.isAvailable():
        return False
    season = comp7LightController.getCurrentSeason()
    if not season:
        return False
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    return settings.get(COMP7_LIGHT_LAST_SEASON) != season.getNumber()


@dependency.replace_none_kwargs(comp7LightController=IComp7LightController)
def updateComp7LightLastSeason(comp7LightController=None):
    season = comp7LightController.getCurrentSeason(includePreannounced=True)
    if not season:
        return
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    settings[COMP7_LIGHT_LAST_SEASON] = season.getNumber()
    AccountSettings.setUIFlag(COMP7_LIGHT_UI_SECTION, settings)
