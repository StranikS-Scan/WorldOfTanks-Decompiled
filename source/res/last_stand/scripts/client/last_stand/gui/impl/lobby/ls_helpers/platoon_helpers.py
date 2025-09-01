# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_helpers/platoon_helpers.py
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.prb_control.entities.base.unit.entity import UnitEntity
from gui.impl import backport
from gui.impl.gen import R
from last_stand.gui.ls_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand_common.last_stand_constants import UNIT_LS_EXTRA_DATA_KEY, UNIT_DIFFICULTY_LEVELS_KEY

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
                availableQueueTypes = slotInfo.player.extraData.get(UNIT_LS_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
                if queueType in availableQueueTypes:
                    continue
                maxAvailableQueue = max([ q for q in availableQueueTypes ])
                additionalMsg = backport.text(R.strings.last_stand_platoon.platoon.difficulty.maxAvailable(), icon='level_{0}'.format(QUEUE_TYPE_TO_DIFFICULTY_LEVEL[maxAvailableQueue].value))
                slot.update({'additionalMsg': additionalMsg,
                 'isVisibleAdtMsg': True})

        squadSize = unitFullData.unit.getSquadSize() or len(slots)
    return (slots, squadSize)
