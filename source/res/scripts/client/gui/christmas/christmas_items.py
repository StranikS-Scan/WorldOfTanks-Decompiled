# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/christmas/christmas_items.py
from christmas_shared import TOY_TYPE_ID_TO_NAME, TREE_DECORATIONS, TANK_DECORATIONS
from helpers.i18n import makeString
from shared_utils import CONST_CONTAINER

class NY_OBJECT_TYPE(CONST_CONTAINER):
    TANK = 'ny_tank'
    TREE = 'ny_tree'


NY_OBJECT_TO_TOY_TYPE = {NY_OBJECT_TYPE.TREE: TREE_DECORATIONS,
 NY_OBJECT_TYPE.TANK: TANK_DECORATIONS}
TOY_TYPE_TO_NY_OBJECT = {toyType:objType for objType, toyTypes in NY_OBJECT_TO_TOY_TYPE.iteritems() for toyType in toyTypes}

class ChristmasItemInfo(object):

    def __init__(self, item, count, isNew=False):
        self.item = item
        self.count = count
        self.isNew = isNew


class ChristmasItem(object):

    def __init__(self, itemID, info):
        super(ChristmasItem, self).__init__()
        self.id = itemID
        self.__info = info

    @property
    def type(self):
        return self.__info['type']

    @property
    def guiType(self):
        return TOY_TYPE_ID_TO_NAME[self.type]

    @property
    def rank(self):
        return self.__info['rank']

    @property
    def ratingValue(self):
        return self.__info['rating']

    @property
    def targetType(self):
        return TOY_TYPE_TO_NY_OBJECT[self.type]

    def getGuiTypeName(self):
        return makeString('#christmas:toyType/%s' % self.guiType)

    def getIconName(self):
        return '%d.png' % self.id

    def getRankIconName(self):
        return '%d.png' % self.rank

    def getNextRankIconName(self):
        return '%d.png' % (self.rank + 1)
