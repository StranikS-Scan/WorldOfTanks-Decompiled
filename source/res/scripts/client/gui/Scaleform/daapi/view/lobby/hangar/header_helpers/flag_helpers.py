# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/flag_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
FLAG_BY_QUEST_TYPE = {HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_VINOUS,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_RED,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_BLUE,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_KHACKI,
 HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_ROYALE: RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_EPIC_STEELHUNTER}

class LabelState(object):
    ACTIVE = 'active'
    EMPTY = 'empty'
    INACTIVE = 'inactive'
    ALL_DONE = 'all_done'


def getActiveQuestLabel(total, completed):
    return backport.text(R.strings.menu.hangar_header.battle_quests_label.dyn(LabelState.ACTIVE)(), total=total - completed)


def headerQuestFormatterVo(enable, icon, label, questType, flag=None, flagDisabled=None, stateIcon=None, questID=None, isReward=False, tooltip='', isTooltipSpecial=False, isTooltipWulf=False):
    return {'enable': enable,
     'flag': flag or FLAG_BY_QUEST_TYPE[questType],
     'flagDisabled': flagDisabled or RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_GRAY,
     'icon': icon,
     'stateIcon': stateIcon,
     'label': label,
     'questType': questType,
     'questID': str(questID),
     'isReward': isReward,
     'tooltip': tooltip,
     'isTooltipSpecial': isTooltipSpecial,
     'isTooltipWulf': isTooltipWulf}


def wrapQuestGroup(groupID, icon, quests, isRightSide=False):
    return {'groupID': groupID,
     'groupIcon': icon,
     'quests': quests,
     'isRightSide': isRightSide}
