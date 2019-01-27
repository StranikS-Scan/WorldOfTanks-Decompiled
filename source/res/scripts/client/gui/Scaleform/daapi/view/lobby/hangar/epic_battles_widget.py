# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/epic_battles_widget.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.Scaleform.daapi.view.meta.EpicBattlesWidgetMeta import EpicBattlesWidgetMeta
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n, int2roman
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
EpicBattlesWidgetVO = namedtuple('EpicBattlesWidgetVO', ('skillPoints', 'calendarStatus', 'canPrestige', 'showAlert', 'epicMetaLevelIconData'))
EpicBattlesWidgetTooltipVO = namedtuple('EpicBattlesWidgetTooltipVO', 'progressBarData')
CalendarStatusVO = namedtuple('CalendarStatusVO', ('alertIcon', 'buttonIcon', 'buttonLabel', 'buttonVisible', 'buttonTooltip', 'statusText', 'popoverAlias', 'bgVisible', 'shadowFilterVisible'))

class EpicBattlesWidget(EpicBattlesWidgetMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def onWidgetClick(self):
        self.epicMetaGameCtrl.openURL()

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def onChangeServerClick(self):
        event_dispatcher.showEpicBattlesPrimeTimeWindow()

    def update(self):
        self.as_setDataS(self._buildVO()._asdict())

    def _buildVO(self):
        pPrestigeLevel, pLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        maxMetaLevel = self.epicMetaGameCtrl.getMaxPlayerLevel()
        isEpicEnabled = self.lobbyContext.getServerSettings().isEpicBattleEnabled()
        showAlert = not self.epicMetaGameCtrl.isInPrimeTime() and isEpicEnabled
        return EpicBattlesWidgetVO(skillPoints=self.epicMetaGameCtrl.getSkillPoints(), calendarStatus=self.__getStatusBlock()._asdict(), canPrestige=pLevel == maxMetaLevel, showAlert=showAlert, epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pLevel))

    def __getStatusBlock(self):
        status, timeLeft, _ = self.epicMetaGameCtrl.getPrimeTimeStatus()
        showPrimeTimeAlert = status != PRIME_TIME_STATUS.AVAILABLE
        hasAvailableServers = self.epicMetaGameCtrl.hasAvailablePrimeTimeServers()
        return CalendarStatusVO(alertIcon=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=i18n.makeString(EPIC_BATTLE.WIDGETALERTMESSAGEBLOCK_BUTTON), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=self.__getAlertStatusText(timeLeft, hasAvailableServers), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert)

    def __getAlertStatusText(self, timeLeft, hasAvailableServers):
        if hasAvailableServers:
            alertStr = _ms(EPIC_BATTLE.WIDGETALERTMESSAGEBLOCK_SOMEPERIPHERIESHALT, serverName=self.__connectionMgr.serverUserNameShort)
        else:
            currSeason = self.epicMetaGameCtrl.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            isCycleNow = currSeason and currSeason.hasActiveCycle(currTime)
            if isCycleNow:
                if self.__connectionMgr.isStandalone():
                    key = EPIC_BATTLE.WIDGETALERTMESSAGEBLOCK_SINGLEMODEHALT
                else:
                    key = EPIC_BATTLE.WIDGETALERTMESSAGEBLOCK_ALLPERIPHERIESHALT
                timeLeftStr = time_utils.getTillTimeString(timeLeft, EPIC_BATTLE.STATUS_TIMELEFT)
                alertStr = _ms(key, time=timeLeftStr)
            else:
                prevSeason = self.epicMetaGameCtrl.getCurrentSeason() or self.epicMetaGameCtrl.getPreviousSeason()
                if prevSeason is not None:
                    prevCycle = prevSeason.getLastActiveCycleInfo(currTime)
                    if prevCycle is not None:
                        cycleId = prevCycle.getEpicCycleNumber()
                        alertStr = _ms(EPIC_BATTLE.WIDGETALERTMESSAGEBLOCK_NOCYCLEMESSAGE, cycle=cycleId)
                    else:
                        alertStr = ''
                else:
                    alertStr = ''
        return text_styles.vehicleStatusCriticalText(alertStr)


class EpicBattlesWidgetTooltip(BlocksTooltipData):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, context):
        super(EpicBattlesWidgetTooltip, self).__init__(context, TOOLTIP_TYPE.EPIC_META_LEVEL_PROGRESS_INFO)
        self._setWidth(width=358)
        self._setContentMargin(top=17)
        self._setMargins(afterBlock=4, afterSeparator=21)

    def _packBlocks(self):
        serverSettings = dependency.instance(ILobbyContext).getServerSettings()
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        maxMetaLevel = self.epicMetaGameCtrl.getMaxPlayerLevel()
        maxPrestigeRewardLevel = serverSettings.epicMetaGame.metaLevel.get('maxPrestigeRewardLevel', None)
        maxPrestigeInSeason = self.epicMetaGameCtrl.getStageLimit()
        famePtsToProgress = self.epicMetaGameCtrl.getPointsProgressForLevel(pMetaLevel)
        boundaryTime, isNow = self.epicMetaGameCtrl.getCurrentCycleInfo()
        blocks = super(EpicBattlesWidgetTooltip, self)._packBlocks()
        cycleID = self.epicMetaGameCtrl.getCurrentSeason().getCycleInfo().getEpicCycleNumber()
        if isNow:
            title = text_styles.highTitle(_ms(TOOLTIPS.EPICBATTLEWIDGET_HEADER, season=cycleID))
        else:
            title = text_styles.highTitle(_ms(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_HEADER))
        if pPrestigeLevel == 0:
            desc = text_styles.main(_ms(TOOLTIPS.EPICBATTLEWIDGET_DESC_NOPRESTIGE, level=pMetaLevel))
        elif pPrestigeLevel == maxPrestigeRewardLevel:
            desc = text_styles.main(_ms(TOOLTIPS.EPICBATTLEWIDGET_DESC_MAXPRESTIGE, prestige=int2roman(pPrestigeLevel), maxPrestige=int2roman(maxPrestigeRewardLevel)))
        else:
            desc = text_styles.main(_ms(TOOLTIPS.EPICBATTLEWIDGET_DESC_NORMAL, prestige=int2roman(pPrestigeLevel), maxPrestige=int2roman(maxPrestigeInSeason), level=pMetaLevel))
        blocks.append(formatters.packTitleDescBlock(title=title, desc=desc, gap=1))
        if pPrestigeLevel < maxPrestigeInSeason and pMetaLevel < maxMetaLevel:
            items = []
            items.append(formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.EPICBATTLESWIDGET_FAMEPOINTS), useHtml=True))
            items.append(formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_EPICBATTLES_FAME_POINT_TINY, width=24, height=24, vSpace=-7), text_styles.main(text_styles.concatStylesWithSpace(text_styles.neutral(str(pFamePts)), '/', str(famePtsToProgress)))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=-22, right=7)))
            data = EpicBattlesWidgetTooltipVO(progressBarData={'value': pFamePts,
             'maxValue': famePtsToProgress})._asdict()
            items.append(formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_PROGRESS_BLOCK_LINKAGE, data=data, padding=formatters.packPadding(left=2, top=-2)))
            items.append(formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.EPICBATTLESWIDGET_FAMEPOINTSDESCRIPTION, level=text_styles.neutral(_ms(TOOLTIPS.EPICBATTLESWIDGET_FAMEPOINTSTOLEVEL, level=str(pMetaLevel + 1))), famePoints=text_styles.neutral(str(famePtsToProgress - pFamePts)))), useHtml=True, padding=formatters.packPadding(top=21)))
            blocks.append(formatters.packBuildUpBlockData(blocks=items, padding=formatters.packPadding(bottom=10)))
        elif pPrestigeLevel == maxPrestigeRewardLevel:
            blocks.append(formatters.packTextBlockData(text=text_styles.neutral(TOOLTIPS.EPICBATTLEWIDGET_INFO_MAXPRESTIGE), padding=formatters.packPadding(top=-5, bottom=14)))
        elif pPrestigeLevel == maxPrestigeInSeason:
            prestigeStr = _ms(TOOLTIPS.EPICBATTLEWIDGET_INFO_PRESTIGE, prestige=int2roman(pPrestigeLevel))
            blocks.append(formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.EPICBATTLEWIDGET_INFO_MAXPRESTIGEINSEASON, prestigeStr=text_styles.neutral(prestigeStr), season=str(cycleID), nextSeason=str(cycleID + 1))), padding=formatters.packPadding(top=-5, bottom=14)))
        elif pMetaLevel == maxMetaLevel:
            blocks.append(formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.EPICBATTLEWIDGET_INFO_MAXLEVEL), padding=formatters.packPadding(top=-5, bottom=14)))
        if isNow and boundaryTime is not None:
            blocks.append(formatters.packTextBlockData(text_styles.concatStylesToSingleLine(text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMELEFT), text_styles.middleTitle(time_utils.getTillTimeString(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(boundaryTime)), MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY))), padding=formatters.packPadding(top=-11)))
        return blocks
