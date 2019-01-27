# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_prime_time_view.py
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import ServerListItemPresenter
from gui.Scaleform.daapi.view.meta.RankedPrimeTimeMeta import RankedPrimeTimeMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import icons, text_styles
from helpers import dependency, i18n
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRankedBattlesController

class RankedServerPresenter(ServerListItemPresenter):
    _periodsController = dependency.descriptor(IRankedBattlesController)

    def _buildTooltip(self):
        return i18n.makeString(TOOLTIPS.RANKED_SERVERNAME, name=self._shortName)


class RankedBattlesPrimeTimeView(RankedPrimeTimeMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    _serverPresenterClass = RankedServerPresenter

    def _getController(self):
        return self.__rankedController

    def _prepareData(self, serverList, serverInfo):
        if len(serverList) == 1:
            serversDDEnabled = False
        else:
            serversDDEnabled = True
        applyButtonLabel = _ms(RANKED_BATTLES.PRIMETIME_APPLYBTN)
        title = text_styles.epicTitle(RANKED_BATTLES.PRIMETIME_TITLE)
        if self._isEnabled:
            if serverInfo:
                serverTimeLeft = serverInfo.getTimeLeft()
                serverName = serverInfo.getName()
            else:
                serverTimeLeft, serverName = (0, '')
            timeLeftStr = time_utils.getTillTimeString(serverTimeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)
            status = text_styles.main(_ms(RANKED_BATTLES.PRIMETIME_STATUS_THISENABLE, server=serverName, time=text_styles.warning(timeLeftStr)))
            mainBackground = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_PRIMETIME_PRIME_TIME_BACK_DEFAULT
            title = text_styles.epicTitle(RANKED_BATTLES.PRIMETIME_TITLEWELCOME)
        else:
            applyButtonLabel = _ms(RANKED_BATTLES.PRIMETIME_CONTINUEBTN)
            status = '{} {}\n{}'.format(icons.alert(-3), text_styles.alert(RANKED_BATTLES.PRIMETIME_STATUS_DISABLEFIRST), text_styles.main(RANKED_BATTLES.PRIMETIME_STATUS_DISABLE))
            mainBackground = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_PRIMETIME_PRIME_TIME_BACK_BW
        return {'title': title,
         'apply': applyButtonLabel,
         'mainBackground': mainBackground,
         'status': status,
         'serversDDEnabled': serversDDEnabled,
         'serverDDVisible': True}

    def _getPrbActionName(self):
        if self._isEnabled:
            prbAction = PREBATTLE_ACTION_NAME.RANKED
        else:
            prbAction = PREBATTLE_ACTION_NAME.RANKED_FORCED
        return prbAction

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.RANKED_FORCED
