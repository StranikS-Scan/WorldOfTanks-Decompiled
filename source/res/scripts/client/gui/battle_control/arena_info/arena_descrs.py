# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_descrs.py
import weakref
import BattleReplay
from constants import IS_DEVELOPMENT
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform import getNecessaryArenaFrameName
from gui.Scaleform.locale.MENU import MENU
from gui.battle_control.arena_info import settings
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.utils import toUpper, functions
from helpers import i18n

def _getDefaultTeamName(isAlly):
    return i18n.makeString(MENU.LOADING_TEAMS_ALLIES) if isAlly else i18n.makeString(MENU.LOADING_TEAMS_ENEMIES)


class IArenaGuiDescription(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    def isPersonalDataSet(self):
        raise NotImplementedError

    def setPersonalData(self, vo):
        raise NotImplementedError

    def isBaseExists(self):
        raise NotImplementedError

    def getTypeName(self, isInBattle=True):
        raise NotImplementedError

    def getDescriptionString(self, isInBattle=True):
        raise NotImplementedError

    def getWinString(self, isInBattle=True):
        raise NotImplementedError

    def getFrameLabel(self):
        raise NotImplementedError

    def getLegacyFrameLabel(self):
        raise NotImplementedError

    def getTeamName(self, team):
        raise NotImplementedError

    def getSmallIcon(self):
        raise NotImplementedError

    def getScreenIcon(self):
        raise NotImplementedError

    def getGuiEventType(self):
        raise NotImplementedError

    def isInvitationEnabled(self):
        raise NotImplementedError

    def isQuestEnabled(self):
        raise NotImplementedError

    def getSelectedQuestIDs(self):
        raise NotImplementedError

    def getSelectedQuestInfo(self):
        raise NotImplementedError


class DefaultArenaGuiDescription(IArenaGuiDescription):
    __slots__ = ('_visitor', '_team', '_questInfo', '_isPersonalDataSet', '_selectedQuestIDs', '_selectedQuestInfo')

    def __init__(self, visitor):
        super(DefaultArenaGuiDescription, self).__init__()
        self._visitor = weakref.proxy(visitor)
        self._team = 0
        self._isPersonalDataSet = False
        self._questInfo = None
        self._selectedQuestIDs = None
        self._selectedQuestInfo = None
        return

    def clear(self):
        self._visitor = None
        return

    def isPersonalDataSet(self):
        return self._isPersonalDataSet

    def setPersonalData(self, vo):
        self._isPersonalDataSet = True
        self._team = vo.team
        if self.isQuestEnabled():
            self._selectedQuestIDs = vo.player.personaMissionIDs
            self._selectedQuestInfo = vo.player.personalMissionInfo

    def isBaseExists(self):
        return functions.isBaseExists(self._visitor.type.getID(), self._team)

    def getTypeName(self, isInBattle=True):
        name = self._visitor.type.getName()
        if isInBattle:
            name = toUpper(name)
        return name

    def getDescriptionString(self, isInBattle=True):
        return i18n.makeString('#menu:loading/battleTypes/{}'.format(self._visitor.getArenaGuiType()))

    def getWinString(self, isInBattle=True):
        return functions.getBattleSubTypeWinText(self._visitor.type.getID(), 1 if self.isBaseExists() else 2)

    def getFrameLabel(self):
        pass

    def getLegacyFrameLabel(self):
        return self._visitor.getArenaGuiType() + 1

    def getTeamName(self, team):
        teamName = _getDefaultTeamName(self._team == team)
        data = self._visitor.getArenaExtraData() or {}
        if 'opponents' in data:
            opponents = data['opponents']
            teamName = opponents.get('%s' % team, {}).get('name', teamName)
        return teamName

    def getSmallIcon(self):
        return self._visitor.getArenaIcon(settings.SMALL_MAP_IMAGE_SF_PATH)

    def getScreenIcon(self):
        return self._visitor.getArenaIcon(settings.SCREEN_MAP_IMAGE_RES_PATH)

    def getRespawnIcon(self):
        return self._visitor.getArenaIcon(settings.RESPAWN_MAP_IMAGE_RES_PATH)

    def getGuiEventType(self):
        pass

    def isInvitationEnabled(self):
        return False

    def isQuestEnabled(self):
        return False

    def getSelectedQuestIDs(self):
        return self._selectedQuestIDs

    def getSelectedQuestInfo(self):
        return self._selectedQuestInfo


class ArenaWithBasesDescription(DefaultArenaGuiDescription):
    __slots__ = ()

    def getDescriptionString(self, isInBattle=True):
        return i18n.makeString('#arenas:type/{}/name'.format(functions.getArenaSubTypeName(self._visitor.type.getID())))

    def getFrameLabel(self):
        return getNecessaryArenaFrameName(functions.getArenaSubTypeName(self._visitor.type.getID()), self.isBaseExists())

    def getLegacyFrameLabel(self):
        return self.getFrameLabel()

    def isInvitationEnabled(self):
        guiVisitor = self._visitor.gui
        replayCtrl = BattleReplay.g_replayCtrl
        return (not replayCtrl.isPlaying or replayCtrl.isBattleSimulation) and (guiVisitor.isRandomBattle() or guiVisitor.isTrainingBattle() and IS_DEVELOPMENT)

    def isQuestEnabled(self):
        guiVisitor = self._visitor.gui
        return guiVisitor.isRandomBattle() or guiVisitor.isTrainingBattle() and IS_DEVELOPMENT


class ArenaWithLabelDescription(DefaultArenaGuiDescription):
    __slots__ = ()

    def getFrameLabel(self):
        return self._visitor.gui.getLabel()

    def getLegacyFrameLabel(self):
        return self.getFrameLabel()


class TutorialBattleDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        pass


class ArenaWithL10nDescription(IArenaGuiDescription):
    __slots__ = ('_l10nDescription', '_decorated')

    def __init__(self, decorated, l10nDescription):
        super(ArenaWithL10nDescription, self).__init__()
        self._decorated = decorated
        self._l10nDescription = l10nDescription

    def clear(self):
        self._decorated.clear()

    def isPersonalDataSet(self):
        self._decorated.isPersonalDataSet()

    def setPersonalData(self, vo):
        self._decorated.setPersonalData(vo)

    def isBaseExists(self):
        return self._decorated.isBaseExists()

    def getTypeName(self, isInBattle=True):
        return self._decorated.getTypeName(isInBattle)

    def getDescriptionString(self, isInBattle=True):
        return self._l10nDescription

    def getWinString(self, isInBattle=True):
        return self._decorated.getWinString()

    def getFrameLabel(self):
        return self._decorated.getFrameLabel()

    def getLegacyFrameLabel(self):
        return self._decorated.getFrameLabel()

    def getTeamName(self, team):
        return self._decorated.getTeamName(team)

    def getSmallIcon(self):
        return self._decorated.getSmallIcon()

    def getScreenIcon(self):
        return self._decorated.getScreenIcon()

    def getGuiEventType(self):
        return self._decorated.getGuiEventType()

    def isInvitationEnabled(self):
        return self._decorated.isInvitationEnabled()

    def isQuestEnabled(self):
        return self._decorated.isQuestEnabled()

    def getSelectedQuestIDs(self):
        return self._decorated.getSelectedQuestIDs()

    def getSelectedQuestInfo(self):
        return self._decorated.getSelectedQuestInfo()


class BootcampBattleDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        lessonId = self._visitor.getArenaExtraData().get('lessonId', 0)
        return i18n.makeString('#arenas:type/{}/description{}'.format(functions.getArenaSubTypeName(self._visitor.type.getID()), lessonId))

    def getScreenIcon(self):
        return settings.DEFAULT_SCREEN_MAP_IMAGE_RES_PATH


class BattleRoyaleDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getScreenIcon(self):
        return settings.DEFAULT_SCREEN_MAP_IMAGE_RES_PATH

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.arenas.c_250_br_battle_city2_1.description())


class BobDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.bob.battleLoading.winText())


class EpicBattlesDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        return functions.getBattleSubTypeWinText(self._visitor.type.getID(), self._team)

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying or replayCtrl.isBattleSimulation

    def getTeamName(self, team):
        from epic_constants import EPIC_BATTLE_TEAM_ID
        from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
        return EPIC_BATTLE.TEAM1NAME if team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER else EPIC_BATTLE.TEAM2NAME


def createDescription(arenaVisitor):
    guiVisitor = arenaVisitor.gui
    if guiVisitor.isRandomBattle() or guiVisitor.isTrainingBattle():
        description = ArenaWithBasesDescription(arenaVisitor)
    elif guiVisitor.isTutorialBattle():
        description = TutorialBattleDescription(arenaVisitor)
    elif guiVisitor.isBootcampBattle():
        description = BootcampBattleDescription(arenaVisitor)
    elif guiVisitor.isInEpicRange():
        description = EpicBattlesDescription(arenaVisitor)
    elif guiVisitor.isBattleRoyale():
        description = BattleRoyaleDescription(arenaVisitor)
    elif guiVisitor.isBobBattle():
        description = BobDescription(arenaVisitor)
    elif guiVisitor.hasLabel():
        description = ArenaWithLabelDescription(arenaVisitor)
    else:
        description = DefaultArenaGuiDescription(arenaVisitor)
    l10nDescription = getPrebattleFullDescription(arenaVisitor.getArenaExtraData() or {})
    if l10nDescription:
        description = ArenaWithL10nDescription(description, l10nDescription)
    return description
