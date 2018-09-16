# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesSkillView.py
from collections import namedtuple
import SoundGroups
from AvatarInputHandler.mathUtils import clamp
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.epicBattle.battle_ability_tooltip_params import g_battleAbilityParamsRenderers
from gui.Scaleform.daapi.view.meta.EpicBattlesSkillViewMeta import EpicBattlesSkillViewMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from helpers import dependency, int2roman
from helpers import i18n
from items import vehicles
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
_SKILL_LEVEL_TEXTS = ['I',
 'II',
 'III',
 'IV',
 'V']
EpicBattlesSkillViewVO = namedtuple('EpicBattlesSkillViewVO', ('skillPoints', 'skills', 'skillsLabel', 'header', 'headerBig', 'showSkillPoints', 'skillInfo', 'backgroundImageSrc'))
EpicBattleSkillVO = namedtuple('EpicBattleSkillVO', ('skillID', 'level', 'maxLevel', 'title', 'smallTitle', 'desc', 'label', 'skillLevelLabels', 'iconUrl'))

class EpicBattlesSkillView(LobbySubView, EpicBattlesSkillViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx=None):
        super(EpicBattlesSkillView, self).__init__()
        self.__selectedSkill = None
        return

    def onEscapePress(self):
        self.__back()

    def onSkillUpgrade(self, skillID):
        self.epicMetaGameCtrl.increaseSkillLevel(skillID)
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_ABILITY_UPGRADE)

    def onBackBtnClick(self):
        self.__back()

    def onSelectSkillBtnClick(self, skillID):
        self.__selectedSkill = skillID
        self.as_setSelectedSkillS(skillID)
        self.__updateSkillDataBlock(skillID)

    def onSkillOverLevel(self, skillID, level):
        self.__updateSkillDataBlock(skillID, level)
        SoundGroups.g_instance.playSound2D('highlight')

    def _populate(self):
        super(EpicBattlesSkillView, self)._populate()
        self.epicMetaGameCtrl.onUpdated += self.__updateData
        self.__selectedSkill = 1
        self.as_setDataS(self._packSkillViewVO())
        self.as_setSelectedSkillS(self.__selectedSkill)
        self.__updateSkillDataBlock(self.__selectedSkill)

    def _dispose(self):
        self.epicMetaGameCtrl.onUpdated -= self.__updateData
        super(EpicBattlesSkillView, self)._dispose()

    @staticmethod
    def _getLevelStr(level):
        romanLvl = int2roman(level)
        levelStr = text_styles.main(i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LEVEL, lvl=romanLvl))
        return levelStr

    def _packSkillViewVO(self):
        unspentSkillPoints = self.epicMetaGameCtrl.getSkillPoints()
        showSkillPoint = unspentSkillPoints > 0
        data = EpicBattlesSkillViewVO(skillPoints=unspentSkillPoints, skills=[], showSkillPoints=showSkillPoint, header=text_styles.superPromoTitle(EPIC_BATTLE.METAABILITYSCREEN_MANAGE_RESERVES_HEADER), headerBig=text_styles.grandTitle(EPIC_BATTLE.METAABILITYSCREEN_MANAGE_RESERVES_HEADER), skillsLabel=self.__getUnspentPointsStr(showSkillPoint), skillInfo=self._packSkillInfo(), backgroundImageSrc=RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BLUR_BG)._asdict()
        skillLvls = self.epicMetaGameCtrl.getSkillLevels()
        allSkills = self.epicMetaGameCtrl.getSkillInformation()
        for skillID, skillInfo in allSkills.iteritems():
            lvl = skillLvls[skillID] if skillID in skillLvls else 0
            icon = RES_ICONS.getEpicBattlesSkillIcon('176x176', skillInfo.levels[max(1, lvl)].icon)
            name = skillInfo.levels[max(1, lvl)].name
            descr = skillInfo.levels[max(1, lvl)].longDescr
            if lvl == 0:
                label = text_styles.standard(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_NOT_UNLOCKED)
            else:
                label = self._getLevelStr(lvl)
            data['skills'].append(EpicBattleSkillVO(skillID=skillID, level=lvl, maxLevel=len(skillInfo.levels), title=text_styles.highTitle(name), smallTitle=text_styles.middleTitle(name), desc=descr, label=label, skillLevelLabels=_SKILL_LEVEL_TEXTS, iconUrl=icon)._asdict())

        return data

    def _packSkillViewVODiff(self, diff):
        data = dict()
        if 'abilities' in diff:
            data['skills'] = []
            skillLvls = self.epicMetaGameCtrl.getSkillLevels()
            for ability in diff['abilities']:
                lvl = skillLvls.get(ability, 0)
                data['skills'].append({'skillID': ability,
                 'level': lvl,
                 'label': self._getLevelStr(lvl)})

        if 'abilityPts' in diff:
            data['skillPoints'] = diff['abilityPts']
        if 'metaLevel' in diff:
            _, newlvl, newXp = diff['metaLevel']
            maxPts = self.epicMetaGameCtrl.getPointsProgessForLevel(newlvl)
            percentage = 1.0 * newXp / (1.0 * maxPts) if maxPts > 0 else 0
            data['metaLevel'] = newlvl
            data['xpProgress'] = percentage
        return data

    def __updateData(self, diff):
        self.__updateSkillDataBlock(self.__selectedSkill)
        self.as_updateDataS(self._packSkillViewVODiff(diff))

    def __updateSkillDataBlock(self, skillID, level=None):
        skillInfo = self.epicMetaGameCtrl.getSkillInformation()[skillID]
        currentLvl = self.epicMetaGameCtrl.getSkillLevels().get(skillID, 1)
        specLevel = clamp(1, skillInfo.maxLvl, int(level) if level else currentLvl)
        eqs = vehicles.g_cache.equipments()
        levels = skillInfo.levels
        curLvlEq = eqs[levels[currentLvl].eqID]
        specLvlEq = eqs[levels[specLevel].eqID]
        bodyBlocks = []
        for tooltipInfo in eqs[skillInfo.levels[currentLvl].eqID].tooltipInformation:
            renderer = g_battleAbilityParamsRenderers.get(tooltipInfo.renderer, None)
            if renderer:
                renderer(bodyBlocks, curLvlEq, specLvlEq, (eqs[lvl.eqID] for lvl in levels.itervalues()), tooltipInfo.identifier, tooltipInfo.name)

        bodyBlock = formatters.packBuildUpBlockData(bodyBlocks, gap=15)
        self.as_setSkillDataBlockS(bodyBlock)
        return

    def __getUnspentPointsStr(self, showSkillPoint):
        return text_styles.highlightText(EPIC_BATTLE.METAABILITYSCREEN_UNSPENT_POINTS) if showSkillPoint else text_styles.tutorial(EPIC_BATTLE.METAABILITYSCREEN_GET_SKILL_POINTS)

    def __back(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def _packSkillInfo(self):
        return {'upgradeBtnLoc': i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_UPGRADE_SKILL),
         'acquireBtnLoc': i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ACQUIRE_SKILL),
         'abilityMaxLevelTxtLoc': text_styles.neutral(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_MAX_LEVEL),
         'abilityLockedTxtLoc': text_styles.alert(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LOCKED),
         'abilityNotPointsTxtLoc': text_styles.alert(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_NOT_POINTS),
         'statsTitleLoc': text_styles.highTitle('{}{}'.format(i18n.makeString(EPIC_BATTLE.ABILITYINFO_PROPERTIES), i18n.makeString(COMMON.COMMON_COLON)))}
