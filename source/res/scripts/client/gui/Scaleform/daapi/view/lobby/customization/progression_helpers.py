# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/progression_helpers.py
import binascii
import logging
import struct
from collections import namedtuple
from constants import EVENT_TYPE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import formatters
from gui.server_events.events_helpers import MISSIONS_STATES
from helpers import dependency
from helpers import int2roman
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

def makeEventID(itemIntCD, vehicleIntCD):
    return binascii.hexlify(struct.pack('II', itemIntCD, vehicleIntCD))


def parseEventID(eventID):
    return struct.unpack('II', binascii.unhexlify(eventID))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getProgressionPostBattleInfo(itemIntCD, vehicleIntCD, progressionData, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehicleIntCD)
    item = itemsCache.items.getItemByCD(itemIntCD)
    level = progressionData.get('level')
    if level is None:
        return
    else:
        progress = progressionData.get('progress')
        inProgress = progress is not None
        if level > 1:
            statusTooltip = backport.text(R.strings.tooltips.quests.status.customizationProgression.done(), name=item.userName, level=int2roman(level))
        else:
            statusTooltip = backport.text(R.strings.tooltips.quests.status.customizationProgression.doneFirst(), name=item.userName)
        questInfo = {'questID': makeEventID(itemIntCD, vehicleIntCD),
         'eventType': EVENT_TYPE.C11N_PROGRESSION,
         'status': MISSIONS_STATES.IN_PROGRESS if inProgress else MISSIONS_STATES.COMPLETED,
         'description': backport.text(R.strings.battle_results.customizationProgress.descr(), level=int2roman(level + 1) if inProgress else int2roman(level), name=item.userName),
         'statusTooltip': statusTooltip}
        isLinkEnabled, linkBtnTooltip = getC11nProgressionLinkBtnParams(vehicle)
        info = {'questInfo': questInfo,
         'linkBtnEnabled': isLinkEnabled,
         'linkBtnTooltip': backport.text(linkBtnTooltip)}
        if inProgress:
            info['progressList'] = __makeProgressList(item, level, progressionData)
        else:
            info['awards'] = __makeAwardsVO(item, level, vehicleIntCD)
        return info


C11nProgressionLinkBtnParams = namedtuple('C11nProgressionLinkBtnParams', ('isLinkEnabled', 'linkBtnTooltip'))

def getC11nProgressionLinkBtnParams(vehicle):
    isLinkEnabled = vehicle.isCustomizationEnabled()
    linkBtnTooltip = R.strings.tooltips.quests.linkBtn.customizationProgression
    linkBtnTooltip = linkBtnTooltip.enabled() if isLinkEnabled else linkBtnTooltip.disabled()
    return C11nProgressionLinkBtnParams(isLinkEnabled, linkBtnTooltip)


def __makeAwardsVO(item, level, vehicleIntCD):
    count = item.descriptor.progression.autoGrantCount
    if count < 1:
        return []
    if level > 1:
        bonusDesc = backport.text(R.strings.battle_results.customizationProgress.award.newLevel(), name=item.userName, level=level)
    else:
        bonusDesc = backport.text(R.strings.battle_results.customizationProgress.award.received(), name=item.userName, count=backport.text(R.strings.vehicle_customization.elementBonus.factor(), count=count))
    award = {'intCD': item.intCD,
     'texture': item.icon,
     'value': count,
     'showPrice': False,
     'description': bonusDesc,
     'vehicleIntCD': vehicleIntCD}
    return formatters.todict([formatters.packCustomizations([award])])


def __makeProgressList(item, level, progressionData):
    progressList = []
    conditions = item.progressionConditions[level + 1]
    for path, (diff, progress) in progressionData['progress'].iteritems():
        idx = 1
        condition = None
        for c in conditions:
            if c['path'] == path:
                condition = c
                break
            idx += 1

        if condition is None:
            _logger.warning('Invalid condition path: %s for item: %s of level: %s', path, item, level)
            continue
        maxProgress = float(condition['value'])
        diff -= max(0, progress - maxProgress)
        if diff <= 0:
            continue
        progress = min(progress, maxProgress)
        diff = min(diff, progress)
        progressList.append(__makeProgressVO(conditionId=idx, description=condition['description'], maxProgress=condition['value'], currentProgress=progress, progressDiff=diff))

    return progressList


def __makeProgressVO(conditionId, description, maxProgress, currentProgress, progressDiff):
    return {'progrTooltip': None,
     'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
     'maxProgrVal': float(maxProgress),
     'currentProgrVal': float(currentProgress),
     'description': '{}. {}'.format(conditionId, _ms(description)),
     'progressDiff': '+ {}'.format(backport.getIntegralFormat(progressDiff)),
     'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE}
