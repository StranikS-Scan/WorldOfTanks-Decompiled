# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesSkillView.py
from collections import namedtuple
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EpicBattlesSkillViewMeta import EpicBattlesSkillViewMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency
from gui.shared.tooltips import formatters
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from helpers import i18n
from AvatarInputHandler.mathUtils import clamp
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.epicBattle.battle_ability_tooltip_params import g_battleAbilityParamsRenderers
from items import vehicles
EpicBattlesSkillViewVO = namedtuple('EpicBattlesSkillViewVO', ('skillPoints', 'skills', 'backgroundImageSrc'))
EpicBattleSkillVO = namedtuple('EpicBattleSkillVO', ('skillID', 'level', 'maxLevel', 'name', 'desc', 'label', 'frameName'))

class EpicBattlesSkillView(LobbySubView, EpicBattlesSkillViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx=None):
        super(EpicBattlesSkillView, self).__init__()

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onSkillUpgrade(self, skillID):
        self.epicMetaGameCtrl.increaseSkillLevel(skillID)

    def onBackBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onSelectSkillBtnClick(self, skillID):
        self.as_setSelectedSkillS(skillID)
        self.__updateSkillDataBlock(skillID)

    def onSkillOverLevel(self, skillID, level):
        self.__updateSkillDataBlock(skillID, level)

    def _populate(self):
        super(EpicBattlesSkillView, self)._populate()
        self.epicMetaGameCtrl.onUpdated += self.__updateData
        self.as_setDataS(self._packSkillViewVO())
        self.as_setSelectedSkillS(1)
        self.__updateSkillDataBlock(1)

    def _dispose(self):
        self.epicMetaGameCtrl.onUpdated -= self.__updateData
        super(EpicBattlesSkillView, self)._dispose()

    def _packSkillViewVO(self):
        data = EpicBattlesSkillViewVO(skillPoints=self.epicMetaGameCtrl.getSkillPoints(), skills=[], backgroundImageSrc='../maps/icons/epicBattles/backgrounds/meta_bg.jpg')._asdict()
        skillLvls = self.epicMetaGameCtrl.getSkillLevels()
        allSkills = self.epicMetaGameCtrl.getSkillInformation()
        for skillID, skillInfo in allSkills.iteritems():
            lvl = skillLvls[skillID] if skillID in skillLvls else 0
            icon = skillInfo.levels[max(1, lvl)].icon
            name = skillInfo.levels[max(1, lvl)].name
            descr = skillInfo.levels[max(1, lvl)].longDescr
            data['skills'].append(EpicBattleSkillVO(skillID=skillID, level=lvl, maxLevel=len(skillInfo.levels), name=name, desc=descr, label=i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_NOT_UNLOCKED) if lvl == 0 else i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LEVEL) + str(lvl), frameName=icon)._asdict())

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
                 'label': i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LEVEL) + str(lvl)})

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
        self.as_updateDataS(self._packSkillViewVODiff(diff))

    def __updateSkillDataBlock(self, skillID, level=None):
        skillInfo = self.epicMetaGameCtrl.getSkillInformation()[skillID]
        currentLvl = self.epicMetaGameCtrl.getSkillLevels().get(skillID, 1)
        specLevel = clamp(1, skillInfo.maxLvl, int(level) if level else currentLvl)
        eqs = vehicles.g_cache.equipments()
        levels = skillInfo.levels
        curLvlEq = eqs[levels[currentLvl].eqID]
        specLvlEq = eqs[levels[specLevel].eqID]
        bodyBlocks = [formatters.packTextParameterBlockData(name='', value=text_styles.middleTitle('{}{}'.format(i18n.makeString(EPIC_BATTLE.ABILITYINFO_PROPERTIES), i18n.makeString(COMMON.COMMON_COLON))), valueWidth=80)]
        for tooltipInfo in eqs[skillInfo.levels[currentLvl].eqID].tooltipInformation:
            renderer = g_battleAbilityParamsRenderers.get(tooltipInfo.renderer, None)
            if renderer:
                renderer(bodyBlocks, curLvlEq, specLvlEq, (eqs[lvl.eqID] for lvl in levels.itervalues()), tooltipInfo.identifier, tooltipInfo.name)

        bodyBlock = formatters.packBuildUpBlockData(bodyBlocks, gap=15)
        self.as_setSkillDataBlockS(bodyBlock)
        return

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()
