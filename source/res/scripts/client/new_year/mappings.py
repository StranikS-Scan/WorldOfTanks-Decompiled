# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/mappings.py
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from itertools import izip as zip

class AnchorNames:
    TREE = 'ChristmasTree'
    SNOWMAN = 'SnowMan'
    HOUSE = 'House'
    LIGHT = 'Light'
    ALL = (TREE,
     SNOWMAN,
     HOUSE,
     LIGHT)


class NewYearObjectIDs:
    TREE_ID = NY_CONSTANTS.SIDE_BAR_TREE_ID
    SNOWMAN_ID = NY_CONSTANTS.SIDE_BAR_SNOWMAN_ID
    HOUSE_ID = NY_CONSTANTS.SIDE_BAR_HOUSE_ID
    LIGHT_ID = NY_CONSTANTS.SIDE_BAR_LIGHT_ID
    ALL = (TREE_ID,
     SNOWMAN_ID,
     HOUSE_ID,
     LIGHT_ID)


class UiTabs:
    TAB_TREE_ID = {'id': NY_CONSTANTS.SIDE_BAR_TREE_ID,
     'linkage': NY_CONSTANTS.NY_LINKAGE_TREE,
     'alias': VIEW_ALIAS.NY_TREE}
    TAB_SBOWMAN_ID = {'id': NY_CONSTANTS.SIDE_BAR_SNOWMAN_ID,
     'linkage': NY_CONSTANTS.NY_LINKAGE_SNOWMAN,
     'alias': VIEW_ALIAS.NY_SNOWMAN}
    TAB_HOUSE_ID = {'id': NY_CONSTANTS.SIDE_BAR_HOUSE_ID,
     'linkage': NY_CONSTANTS.NY_LINKAGE_HOUSE,
     'alias': VIEW_ALIAS.NY_HOUSE}
    TAB_LIHGT_ID = {'id': NY_CONSTANTS.SIDE_BAR_LIGHT_ID,
     'linkage': NY_CONSTANTS.NY_LINKAGE_LIGHT,
     'alias': VIEW_ALIAS.NY_LIGHT}
    ALL = (TAB_TREE_ID,
     TAB_SBOWMAN_ID,
     TAB_HOUSE_ID,
     TAB_LIHGT_ID)


class Mappings:
    ID_TO_ANCHOR = {k:v for k, v in zip(NewYearObjectIDs.ALL, AnchorNames.ALL)}
    ANCHOR_TO_ID = {k:v for k, v in zip(AnchorNames.ALL, NewYearObjectIDs.ALL)}


class UiStates:
    CRAFT_WINDOW = 'craft'
    BREAK_WINDOW = 'break'
    VIEW_ALIASES = {CRAFT_WINDOW: VIEW_ALIAS.LOBBY_NY_CRAFT,
     BREAK_WINDOW: VIEW_ALIAS.LOBBY_NY_BREAK}
