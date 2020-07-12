# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/special_mode_battle/prime_time_view.py
import time
from collections import namedtuple
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase
from gui.Scaleform.daapi.view.lobby.prime_time_servers_data_provider import PrimeTimesServersDataProvider
from gui.shared.formatters import icons, text_styles
from helpers import time_utils
from helpers.i18n import makeString as _ms
LocaleData = namedtuple('LocaleData', ('enableTitle', 'enableWelcomeTitle', 'enableBtnTitle', 'disableTitle', 'disableStatusTitle', 'disableStatusDescr', 'disableBtnTitle'))
ImgsData = namedtuple('ImgsData', ('enableBackground', 'disableBackground'))

class SpecialModePrimeTimeView(PrimeTimeViewBase):

    def _getLocaleData(self):
        raise NotImplementedError

    def _getImgsData(self):
        raise NotImplementedError

    def _getAllServersDP(self):
        primeTimesForDay = self._getController().getPrimeTimesForDay(time.time(), groupIdentical=False)
        return PrimeTimesServersDataProvider(primeTimesForDay=primeTimesForDay)

    def _prepareData(self, serverList, serverName, serverTimeLeft):
        enableTitle, enableWelcomeTitle, enableBtnTitle, disableTitle, disableStatusTitle, disableStatusDescr, disableBtnTitle = self._getLocaleData()
        enableBackground, disableBackground = self._getImgsData()
        if self._isEnabled:
            timeLeftStr = time_utils.getTillTimeString(serverTimeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)
            status = text_styles.main(_ms(enableTitle, server=serverName, time=text_styles.warning(timeLeftStr)))
            mainBackground = enableBackground
            title = text_styles.epicTitle(enableWelcomeTitle)
            applyButtonLabel = _ms(enableBtnTitle)
        else:
            status = '{} {}\n{}'.format(icons.alert(-3), text_styles.alert(disableStatusTitle), text_styles.main(disableStatusDescr))
            mainBackground = disableBackground
            title = text_styles.epicTitle(disableTitle)
            applyButtonLabel = _ms(disableBtnTitle)
        return {'title': title,
         'apply': applyButtonLabel,
         'mainBackground': mainBackground,
         'status': status,
         'serversDDEnabled': len(serverList) > 1,
         'serverDDVisible': True}

    def _getPrbActionName(self, isEnabled):
        return self._getPrbForcedActionName()

    def _getEndSeasonTime(self):
        raise NotImplementedError

    def _getTimeLeft(self, pID):
        primeTime = self._getController().getPrimeTimes().get(pID)
        if not primeTime:
            return 0
        _, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), self._getEndSeasonTime())
        return timeLeft
