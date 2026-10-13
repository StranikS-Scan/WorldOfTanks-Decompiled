# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_helpers/platoon_helpers.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.prb_control.entities.base.unit.entity import UnitEntity
from gui.impl import backport
from gui.impl.gen import R
from halloween.gui.halloween_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from halloween_common.halloween_constants import UNIT_HALLOWEEN_EXTRA_DATA_KEY, UNIT_DIFFICULTY_LEVELS_KEY

def getPlatoonSlotsData(entity, queueType):
    slots = {}
    squadSize = 0
    if isinstance(entity, UnitEntity):
        unitFullData = entity.getUnitFullData(entity.getID())
        if unitFullData.unit is None:
            return (slots, squadSize)
        _, slots = vo_converters.makeSlotsVOs(entity, entity.getID(), withPrem=True)
        for slotInfo in unitFullData.slotsIterator:
            if slotInfo.player is None:
                continue
            for slot in slots:
                player = slot['player']
                if player is None:
                    continue
                if slotInfo.player.dbID != player['dbID']:
                    continue
                availableQueueTypes = slotInfo.player.extraData.get(UNIT_HALLOWEEN_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
                if queueType in availableQueueTypes:
                    continue
                additionalMsg = backport.text(R.strings.halloween_platoon.platoon.difficulty.maxAvailable(), icon='level_{0}'.format(QUEUE_TYPE_TO_DIFFICULTY_LEVEL[availableQueueTypes[-1]].value))
                slot.update({'additionalMsg': additionalMsg,
                 'isVisibleAdtMsg': True})

        squadSize = unitFullData.unit.getSquadSize() or len(slots)
    return (slots, squadSize)
