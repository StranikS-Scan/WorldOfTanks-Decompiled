# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_descrs.py
from collections import namedtuple
import weakref
import BattleReplay
from constants import IS_DEVELOPMENT
from gui.Scaleform import getNecessaryArenaFrameName
from gui.Scaleform.locale.ARENAS import ARENAS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.MENU import MENU
from gui.battle_control.arena_info import settings
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.shared.formatters import text_styles
from gui.shared.utils import toUpper, functions
from helpers import i18n
_QuestInfo = namedtuple('_QuestInfo', 'name, condition, additional')

def _makeQuestInfo(quest):
    condition = '\n'.join((text_styles.middleTitle(INGAME_GUI.POTAPOVQUESTS_TIP_MAINHEADER), text_styles.main(quest.getUserMainCondition())))
    additional = '\n'.join((text_styles.middleTitle(INGAME_GUI.POTAPOVQUESTS_TIP_ADDITIONALHEADER), text_styles.main(quest.getUserAddCondition())))
    return _QuestInfo(quest.getUserName(), condition, additional)


def _getDefaultTeamName(isAlly):
    if isAlly:
        return i18n.makeString(MENU.LOADING_TEAMS_ALLIES)
    else:
        return i18n.makeString(MENU.LOADING_TEAMS_ENEMIES)


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

    def getQuestInfo(self):
        raise NotImplementedError

    def makeQuestInfo(self, vo):
        raise NotImplementedError


class DefaultArenaGuiDescription(IArenaGuiDescription):
    __slots__ = ('_visitor', '_team', '_questInfo', '_isPersonalDataSet')

    def __init__(self, visitor):
        super(DefaultArenaGuiDescription, self).__init__()
        self._visitor = weakref.proxy(visitor)
        self._team = 0
        self._isPersonalDataSet = False
        self._questInfo = None
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
            self._questInfo = self.makeQuestInfo(vo)

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

    def getGuiEventType(self):
        pass

    def isInvitationEnabled(self):
        return False

    def isQuestEnabled(self):
        return False

    def getQuestInfo(self):
        return self._questInfo

    def makeQuestInfo(self, vo):
        return None


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

    def makeQuestInfo(self, vo):
        pQuests = vo.player.getRandomPotapovQuests()
        if pQuests:
            return _makeQuestInfo(pQuests[0])
        else:
            return _QuestInfo(i18n.makeString(INGAME_GUI.POTAPOVQUESTS_TIP_NOQUESTS_VEHICLETYPE), '', '')


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

    def getQuestInfo(self):
        return self._decorated.getQuestInfo()

    def makeQuestInfo(self, vo):
        return self._decorated.makeQuestInfo()


class FalloutBattlesDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        if isInBattle and self._visitor.gui.isFalloutMultiTeam():
            return i18n.makeString(ARENAS.TYPE_FALLOUTMUTLITEAM_DESCRIPTION)
        else:
            return i18n.makeString('#arenas:type/{}/description'.format(functions.getArenaSubTypeName(self._visitor.type.getID())))

    def getGuiEventType(self):
        pass

    def isQuestEnabled(self):
        return True

    def makeQuestInfo(self, vo):
        pQuests = vo.player.getFalloutPotapovQuests()
        if pQuests:
            return _makeQuestInfo(pQuests[0])
        else:
            return _QuestInfo(i18n.makeString(INGAME_GUI.POTAPOVQUESTS_TIP_NOQUESTS_BATTLETYPE), '', '')


class BootcampBattleDescription(ArenaWithLabelDescription):
    __slots__ = ()

    def getWinString(self, isInBattle=True):
        lessonId = self._visitor.getArenaExtraData().get('lessonId', 0)
        return i18n.makeString('#arenas:type/{}/description{}'.format(functions.getArenaSubTypeName(self._visitor.type.getID()), lessonId))


def createDescription(arenaVisitor):
    guiVisitor = arenaVisitor.gui
    if guiVisitor.isRandomBattle() or guiVisitor.isTrainingBattle():
        description = ArenaWithBasesDescription(arenaVisitor)
    elif guiVisitor.isTutorialBattle():
        description = TutorialBattleDescription(arenaVisitor)
    elif guiVisitor.isFalloutBattle():
        description = FalloutBattlesDescription(arenaVisitor)
    elif guiVisitor.isBootcampBattle():
        description = BootcampBattleDescription(arenaVisitor)
    elif guiVisitor.hasLabel():
        description = ArenaWithLabelDescription(arenaVisitor)
    else:
        description = DefaultArenaGuiDescription(arenaVisitor)
    l10nDescription = getPrebattleFullDescription(arenaVisitor.getArenaExtraData() or {})
    if l10nDescription:
        description = ArenaWithL10nDescription(description, l10nDescription)
    return description
