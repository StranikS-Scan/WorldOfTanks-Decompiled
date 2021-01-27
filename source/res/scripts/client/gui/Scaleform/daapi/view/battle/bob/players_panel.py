# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/players_panel.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.BobPlayersPanelMeta import BobPlayersPanelMeta
from gui.bob.bob_helpers import getShortSkillName
from gui.impl import backport
from gui.impl.gen import R
_DEFAULT_NAME = 'default'

def _isBattleStarted(arenaPeriod):
    return arenaPeriod == ARENA_PERIOD.BATTLE or arenaPeriod == ARENA_PERIOD.AFTERBATTLE


class BobPlayersPanel(BobPlayersPanelMeta):

    def _populate(self):
        super(BobPlayersPanel, self)._populate()
        bobCtrl = self.guiSessionProvider.dynamic.bob
        bobCtrl.onSkillUpdated += self.__updateSkills
        bobCtrl.onInited += self.__updateSkills
        if bobCtrl.isInited():
            self.__updateSkills()
        arenaPeriod = BigWorld.player().arena.period
        self.as_setBattleStartedS(value=_isBattleStarted(arenaPeriod))
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _dispose(self):
        bobCtrl = self.guiSessionProvider.dynamic.bob
        if bobCtrl is not None:
            bobCtrl.onSkillUpdated -= self.__updateSkills
            bobCtrl.onInited -= self.__updateSkills
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(BobPlayersPanel, self)._dispose()
        return

    def __onArenaPeriodChange(self, arenaPeriod, *_):
        self.as_setBattleStartedS(value=_isBattleStarted(arenaPeriod))

    def __updateSkills(self):
        bobCtrl = self.guiSessionProvider.dynamic.bob
        self.as_setLeftTeamSkillS(*self.__getTeamSkillData(bobCtrl.getAllySkill()))
        self.as_setRightTeamSkillS(*self.__getTeamSkillData(bobCtrl.getEnemySkill()))

    def __getTeamSkillData(self, skillName):
        shortSkillName = getShortSkillName(skillName) if skillName else _DEFAULT_NAME
        skillLabel = backport.text(R.strings.bob.skill.dyn(shortSkillName)())
        skillDescr = backport.text(R.strings.bob.skill.description.dyn(shortSkillName)())
        return (shortSkillName, skillLabel, skillDescr)
