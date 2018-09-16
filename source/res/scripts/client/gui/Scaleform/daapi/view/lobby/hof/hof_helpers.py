# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hof/hof_helpers.py
import Keys
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import dependency
from gui import GUI_SETTINGS, DialogsInterface
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from skeletons.gui.lobby_context import ILobbyContext
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_HOF_COUNTER
NEW_HOF_BUTTONS_IDS = (PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON, PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON)
NEW_ACHIEVEMENTS_BUTTONS_IDS = (PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON, PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON, PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getHofUrl(urlName, lobbyContext=None):
    if lobbyContext is None:
        return
    else:
        try:
            return lobbyContext.getServerSettings().bwHallOfFame.hofHostUrl + GUI_SETTINGS.hallOfFame.get(urlName)
        except (AttributeError, TypeError):
            LOG_CURRENT_EXCEPTION()
            return

        return


def getHofAchievementsRatingUrl():
    return _getHofUrl('achievementsRatingUrl')


def getHofVehiclesRatingUrl():
    return _getHofUrl('vehiclesRatingUrl')


def getHofRatingUrlForVehicle(vehicleCD):
    if vehicleCD is None:
        LOG_DEBUG('vehicleCD should be not None')
        return
    else:
        try:
            return _getHofUrl('vehiclesRatingUrl') + '/' + str(vehicleCD)
        except TypeError:
            LOG_CURRENT_EXCEPTION()
            return

        return


def _calculateCounters(ids):
    count = 0
    for cID in ids:
        if isHofButtonNew(cID):
            count += 1

    return count


def getAchievementsTabCounter():
    return _calculateCounters(NEW_ACHIEVEMENTS_BUTTONS_IDS)


def getHofTabCounter():
    return _calculateCounters(NEW_HOF_BUTTONS_IDS)


def isHofButtonNew(buttonID):
    return _getSettingsFromStorage().get(buttonID)


def setHofButtonOld(buttonID):
    settings = _getSettingsFromStorage()
    if buttonID in settings.keys():
        settings[buttonID] = False
        _setSettingsToStorage(settings)


def _getSettingsFromStorage():
    return AccountSettings.getCounters(NEW_HOF_COUNTER)


def _setSettingsToStorage(value):
    AccountSettings.setCounters(NEW_HOF_COUNTER, value)


def getHofDisabledKeys():
    return ((Keys.KEY_F5,
      True,
      False,
      False,
      False),
     (Keys.KEY_LEFTARROW,
      True,
      True,
      False,
      False),
     (Keys.KEY_NUMPAD4,
      True,
      True,
      False,
      False),
     (Keys.KEY_RIGHTARROW,
      True,
      True,
      False,
      False),
     (Keys.KEY_NUMPAD6,
      True,
      True,
      False,
      False),
     (Keys.KEY_BACKSPACE,
      True,
      False,
      True,
      False),
     (Keys.KEY_F5,
      True,
      False,
      False,
      True),
     (Keys.KEY_HOME,
      True,
      True,
      False,
      False),
     (Keys.KEY_NUMPAD7,
      True,
      True,
      False,
      False),
     (Keys.KEY_0,
      True,
      None,
      None,
      True),
     (Keys.KEY_1,
      True,
      None,
      None,
      True),
     (Keys.KEY_2,
      True,
      None,
      None,
      True),
     (Keys.KEY_3,
      True,
      None,
      None,
      True),
     (Keys.KEY_4,
      True,
      None,
      None,
      True),
     (Keys.KEY_5,
      True,
      None,
      None,
      True),
     (Keys.KEY_6,
      True,
      None,
      None,
      True),
     (Keys.KEY_7,
      True,
      None,
      None,
      True),
     (Keys.KEY_8,
      True,
      None,
      None,
      True),
     (Keys.KEY_9,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD0,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD1,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD2,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD3,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD4,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD5,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD6,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD7,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD8,
      True,
      None,
      None,
      True),
     (Keys.KEY_NUMPAD9,
      True,
      None,
      None,
      True),
     (Keys.KEY_TAB,
      True,
      False,
      False,
      True),
     (Keys.KEY_TAB,
      True,
      False,
      True,
      True),
     (Keys.KEY_PGDN,
      True,
      False,
      False,
      True),
     (Keys.KEY_PGUP,
      True,
      False,
      False,
      True),
     (Keys.KEY_W,
      True,
      False,
      False,
      True),
     (Keys.KEY_F4,
      True,
      False,
      False,
      True),
     (Keys.KEY_T,
      True,
      False,
      True,
      True),
     (Keys.KEY_T,
      True,
      False,
      False,
      True),
     (Keys.KEY_N,
      True,
      False,
      False,
      True),
     (Keys.KEY_H,
      True,
      False,
      False,
      True),
     (Keys.KEY_J,
      True,
      False,
      False,
      True),
     (Keys.KEY_D,
      True,
      False,
      False,
      True),
     (Keys.KEY_DELETE,
      True,
      False,
      True,
      True),
     (Keys.KEY_O,
      True,
      False,
      False,
      True),
     (Keys.KEY_U,
      True,
      False,
      False,
      True),
     (Keys.KEY_EQUALS,
      True,
      False,
      False,
      True),
     (Keys.KEY_ADD,
      True,
      False,
      False,
      True),
     (Keys.KEY_MINUS,
      True,
      False,
      False,
      True),
     (Keys.KEY_NUMPADMINUS,
      True,
      False,
      False,
      True),
     (Keys.KEY_F11,
      True,
      False,
      False,
      False),
     (Keys.KEY_A,
      True,
      False,
      False,
      True))


def showDisabledDialog():
    DialogsInterface.showI18nInfoDialog('hofDisabled', None)
    return


def onServerSettingsChange(browserView, diff):
    if 'hallOfFame' in diff:
        isHofEnabled = diff['hallOfFame'].get('isHofEnabled', False)
        if not isHofEnabled:
            browserView.updateCtx({'selectedAlias': None})
            browserView.onCloseView()
            showDisabledDialog()
    return
