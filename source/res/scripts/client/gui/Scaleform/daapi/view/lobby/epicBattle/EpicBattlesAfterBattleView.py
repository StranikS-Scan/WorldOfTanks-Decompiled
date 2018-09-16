# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesAfterBattleView.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.EpicBattlesAfterBattleViewMeta import EpicBattlesAfterBattleViewMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.utils import toUpper
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
EpicBattlesAfterBattleViewVO = namedtuple('EpicBattlesAfterBattleViewVO', ('awards', 'progress', 'barText', 'currentPrestigeLevel', 'epicMetaLevelIconData', 'rank', 'rankText', 'rankTextBig', 'rankSubText', 'levelUpText', 'levelUpTextBig', 'backgroundImageSrc', 'maxLevel'))

class EpicBattlesAfterBattleView(EpicBattlesAfterBattleViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)
    _MAX_VISIBLE_AWARDS = 8
    _awardsFormatter = CurtailingAwardsComposer(_MAX_VISIBLE_AWARDS)

    def __init__(self, ctx=None):
        super(EpicBattlesAfterBattleView, self).__init__()
        self.__ctx = ctx

    def onIntroStartsPlaying(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_ACHIEVED_RANK)

    def onRibbonStartsPlaying(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED)

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(EpicBattlesAfterBattleView, self)._populate()
        extInfo = self.__ctx['reusableInfo'].personal.avatar.extensionInfo
        epicMetaGame = extInfo['epicMetaGame']
        pPrestigeLevel, pMetaLevel, pFamePts = epicMetaGame.get('metaLevel', (None, None, None))
        _, prevPMetaLevel, prevPFamePts = epicMetaGame.get('prevMetaLevel', (None, None, None))
        mlSettings = dependency.instance(ILobbyContext).getServerSettings().epicMetaGame.metaLevel
        maxMetaLevel = mlSettings.get('maxLevel', 0)
        famePtsToProgress = mlSettings.get('famePtsToProgress', None)
        famePointsReceived = sum(famePtsToProgress[prevPMetaLevel - 1:pMetaLevel - 1]) + pFamePts - prevPFamePts
        achievedRank = extInfo['playerRank'].get('rank', -1)
        rankName = getattr(EPIC_BATTLE, 'RANK_RANK{}'.format(achievedRank))
        achievedRank += 1
        questsProgressData = self.__ctx['reusableInfo'].personal.getQuestsProgress()
        bonuses = sum([ self.eventsCache.getAllQuests().get(q).getBonuses() for q in questsProgressData ], [])
        awardsVO = self._awardsFormatter.getFormattedBonuses(bonuses, size=AWARDS_SIZES.BIG)
        lvlReachedText = EPIC_BATTLE.EPIC_BATTLES_AFTER_BATTLE_LEVEL_UP_MAX_TITLE if pMetaLevel == maxMetaLevel else EPIC_BATTLE.EPIC_BATTLES_AFTER_BATTLE_LEVEL_UP_TITLE
        data = EpicBattlesAfterBattleViewVO(awards=awardsVO, progress=self.__getProgress(pMetaLevel, pFamePts, prevPMetaLevel, prevPFamePts, maxMetaLevel), barText='+' + str(famePointsReceived), currentPrestigeLevel=pPrestigeLevel, epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pMetaLevel), rank=achievedRank, rankText=toUpper(text_styles.heroTitle(rankName)), rankTextBig=toUpper(text_styles.epicTitle(rankName)), rankSubText=text_styles.highTitle(EPIC_BATTLE.EPIC_BATTLES_AFTER_BATTLE_ACHIEVED_RANK), levelUpText=toUpper(text_styles.heroTitle(lvlReachedText)), levelUpTextBig=toUpper(text_styles.epicTitle(lvlReachedText)), backgroundImageSrc=RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG, maxLevel=maxMetaLevel)
        self.as_setDataS(data._asdict())
        return

    def _dispose(self):
        super(EpicBattlesAfterBattleView, self)._dispose()

    def __close(self):
        self.destroy()

    def __getProgress(self, curLevel, curFamePoints, prevLevel, prevFamePoints, maxLevel):
        pLevel = prevLevel + float(prevFamePoints) / float(self.epicMetaGameCtrl.getPointsProgessForLevel(prevLevel)) if prevLevel != maxLevel else maxLevel
        cLevel = curLevel + float(curFamePoints) / float(self.epicMetaGameCtrl.getPointsProgessForLevel(curLevel)) if curLevel != maxLevel else maxLevel
        return (pLevel, cLevel)
