# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/sorts/__init__.py
from collections import namedtuple
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER

class SortType(CONST_CONTAINER):
    DETACHMENT = 'detachment'


class Sorts(CONST_CONTAINER):
    NATION = 'nation'
    EXPERIENCE = 'experience'


RadioButtonSettings = namedtuple('RadioButtonSettings', ('id', 'label', 'isDisable'))

def getDetachmentSorts():
    return {'id': SortType.DETACHMENT,
     'label': R.strings.detachment.toggleSortFilterPopover.group.sort.label(),
     'sorts': [RadioButtonSettings(id=Sorts.NATION, label=R.strings.detachment.toggleSortFilterPopover.radio.nation(), isDisable=False), RadioButtonSettings(id=Sorts.EXPERIENCE, label=R.strings.detachment.toggleSortFilterPopover.radio.experience(), isDisable=False)]}
