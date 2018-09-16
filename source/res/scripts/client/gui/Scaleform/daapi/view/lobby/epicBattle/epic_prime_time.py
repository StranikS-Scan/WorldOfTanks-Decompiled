# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prime_time.py
import time
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase
from gui.Scaleform.daapi.view.lobby.prime_time_servers_data_provider import PrimeTimesServersDataProvider
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import icons, text_styles
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattlesPrimeTimeView(PrimeTimeViewBase):
    epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx=None):
        super(EpicBattlesPrimeTimeView, self).__init__()

    def _getController(self):
        return self.epicController

    def _getAllServersDP(self):
        primeTimesForDay = self.epicController.getPrimeTimesForDay(time.time(), groupIdentical=False)
        return PrimeTimesServersDataProvider(primeTimesForDay=primeTimesForDay)

    def _prepareData(self, serverList, serverName, serverTimeLeft):
        if len(serverList) == 1:
            serversDDEnabled = False
        else:
            serversDDEnabled = True
        applyButtonLabel = _ms(EPIC_BATTLE.PRIMETIME_APPLYBTN)
        title = text_styles.epicTitle(EPIC_BATTLE.PRIMETIME_TITLE)
        if self._isEnabled:
            timeLeftStr = time_utils.getTillTimeString(serverTimeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)
            status = text_styles.main(_ms(EPIC_BATTLE.PRIMETIME_STATUS_THISENABLE, server=serverName, time=text_styles.warning(timeLeftStr)))
            mainBackground = RES_ICONS.MAPS_ICONS_EPICBATTLES_PRIMETIME_PRIME_TIME_BACK_DEFAULT
            title = text_styles.epicTitle(EPIC_BATTLE.PRIMETIME_TITLEWELCOME)
        else:
            applyButtonLabel = _ms(EPIC_BATTLE.PRIMETIME_CONTINUEBTN)
            status = '{} {}\n{}'.format(icons.alert(-3), text_styles.alert(EPIC_BATTLE.PRIMETIME_STATUS_DISABLEFIRST), text_styles.main(EPIC_BATTLE.PRIMETIME_STATUS_DISABLE))
            mainBackground = RES_ICONS.MAPS_ICONS_EPICBATTLES_PRIMETIME_PRIME_TIME_BACK_BW
        return {'title': title,
         'apply': applyButtonLabel,
         'mainBackground': mainBackground,
         'status': status,
         'serversDDEnabled': serversDDEnabled,
         'serverDDVisible': True}

    def _getPrbActionName(self, isEnabled):
        if self._isEnabled:
            prbAction = PREBATTLE_ACTION_NAME.EPIC
        else:
            prbAction = PREBATTLE_ACTION_NAME.EPIC_FORCED
        return prbAction

    def _getTimeLeft(self, pID):
        primeTime = self.epicController.getPrimeTimes().get(pID)
        if not primeTime:
            return 0
        seasonEnd, _ = self.epicController.getSeasonEndTime()
        _, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), seasonEnd)
        return timeLeft

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.EPIC_FORCED
