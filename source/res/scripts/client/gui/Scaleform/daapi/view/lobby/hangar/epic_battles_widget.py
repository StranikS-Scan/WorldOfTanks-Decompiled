# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/epic_battles_widget.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.Scaleform.daapi.view.meta.EpicBattlesWidgetMeta import EpicBattlesWidgetMeta
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n, int2roman
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
EpicBattlesWidgetVO = namedtuple('EpicBattlesWidgetVO', ('skillPoints', 'calendarStatus', 'canPrestige', 'showAlert', 'epicMetaLevelIconData'))
EpicBattlesWidgetTooltipVO = namedtuple('EpicBattlesMetaLevelVO', ('headline', 'description', 'progressText', 'progressBarData'))
CalendarStatusVO = namedtuple('EpicBattlesWidgetVO', ('alertIcon', 'buttonIcon', 'buttonLabel', 'buttonVisible', 'buttonTooltip', 'statusText', 'popoverAlias', 'bgVisible', 'shadowFilterVisible'))

class EpicBattlesWidget(EpicBattlesWidgetMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def onWidgetClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def update(self):
        self.as_setDataS(self._buildVO()._asdict())

    def _buildVO(self):
        status, timeLeft, _ = self.epicMetaGameCtrl.getPrimeTimeStatus()
        showPrimeTimeAlert = status != PRIME_TIME_STATUS.AVAILABLE
        pPrestigeLevel, pLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        maxMetaLevel = self.epicMetaGameCtrl.getMaxPlayerLevel()
        isEpicEnabled = self.lobbyContext.getServerSettings().isEpicBattleEnabled()
        showAlert = not self.epicMetaGameCtrl.isInPrimeTime() and isEpicEnabled and timeLeft > 0
        return EpicBattlesWidgetVO(skillPoints=self.epicMetaGameCtrl.getSkillPoints(), calendarStatus=self.__getStatusBlock(showPrimeTimeAlert, timeLeft)._asdict(), canPrestige=pLevel == maxMetaLevel, showAlert=showAlert, epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pLevel))

    def __getStatusBlock(self, showPrimeTimeAlert, timeLeft):
        return CalendarStatusVO(alertIcon=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON if showPrimeTimeAlert else None, buttonIcon=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, buttonLabel='', buttonVisible=False, buttonTooltip=None, statusText=self.__getAlertStatusText(timeLeft), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert)

    def __getAlertStatusText(self, timeLeft):
        timeLeftStr = ''
        if timeLeft > 0:
            timeLeftStr = time_utils.getTillTimeString(timeLeft, EPIC_BATTLE.STATUS_TIMELEFT)
        return text_styles.vehicleStatusCriticalText(_ms(EPIC_BATTLE.PRIMETIMEALERTMESSAGEBLOCK_MESSAGE, time=timeLeftStr))

    def __getTillTimeString(self, endTime):
        timeDelta = time_utils.getTimeDeltaFromNow(endTime)
        formatter = text_styles.neutral if timeDelta > time_utils.ONE_DAY else text_styles.alert
        return formatter(time_utils.getTillTimeString(timeDelta, EPIC_BATTLE.STATUS_TIMELEFT))


class EpicBattlesWidgetTooltip(BlocksTooltipData):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, context):
        super(EpicBattlesWidgetTooltip, self).__init__(context, TOOLTIP_TYPE.EPIC_META_LEVEL_PROGRESS_INFO)
        self._setWidth(width=353)
        self._setMargins(afterBlock=5, afterSeparator=15)

    def _packBlocks(self):
        serverSettings = dependency.instance(ILobbyContext).getServerSettings()
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        maxMetaLevel = self.epicMetaGameCtrl.getMaxPlayerLevel()
        maxPrestigeLevel = serverSettings.epicMetaGame.metaLevel.get('maxPrestigeLevel', None)
        famePtsToProgress = self.epicMetaGameCtrl.getPointsProgressForLevel(pMetaLevel)
        block = super(EpicBattlesWidgetTooltip, self)._packBlocks()
        title = TOOLTIPS.EPICBATTLEWIDGET_HEADER
        desc = i18n.makeString(TOOLTIPS.EPICBATTLEWIDGET_DESC, prestige=int2roman(pPrestigeLevel + 1), level=pMetaLevel)
        block.append(formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc=text_styles.standard(desc)))
        if pMetaLevel == maxMetaLevel:
            if pPrestigeLevel == maxPrestigeLevel:
                block.append(formatters.packTextBlockData(TOOLTIPS.EPICBATTLEWIDGET_BODY_MAXMETALEVEL_MAXPRESTIGE))
            else:
                block.append(formatters.packTextBlockData(TOOLTIPS.EPICBATTLEWIDGET_BODY_MAXMETALEVEL_PRESTIGE))
        else:
            data = EpicBattlesWidgetTooltipVO(headline=EPIC_BATTLE.EPICBATTLESWIDGETTOOLTIP_FAMEPOINTS, description=EPIC_BATTLE.EPICBATTLESWIDGETTOOLTIP_FAMEPOINTSDESCRIPTION, progressText='{}{}'.format(text_styles.stats(str(pFamePts) + ' / '), str(famePtsToProgress)), progressBarData={'value': pFamePts,
             'maxValue': famePtsToProgress})._asdict()
            block.append(formatters.packBlockDataItem(BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_PROGRESS_BLOCK_LINKAGE, data))
        return block
