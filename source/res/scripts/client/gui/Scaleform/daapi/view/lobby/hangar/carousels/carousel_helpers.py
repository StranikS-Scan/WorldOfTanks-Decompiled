# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/carousel_helpers.py
from gui.impl import backport
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import getTypeUserName
from gui.shared.utils.functions import makeTooltip

def getUnsuitable2queueTooltip(validationResult, resPath):
    header, body = ('', '')
    if validationResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
        levelStr = toRomanRangeString(validationResult.ctx['levels'])
        levelSubStr = backport.text(resPath.vehLvl.levelSubStr(), levels=levelStr)
        header = backport.text(resPath.vehLvl.header())
        body = backport.text(resPath.vehLvl.body(), levelSubStr=levelSubStr)
    elif validationResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE:
        typeSubStr = text_styles.neutral(validationResult.ctx['forbiddenType'])
        header = backport.text(resPath.vehType.header())
        body = backport.text(resPath.vehType.body(), forbiddenType=typeSubStr)
    elif validationResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS:
        classSubStr = text_styles.neutral(getTypeUserName(validationResult.ctx['forbiddenClass'], False))
        header = backport.text(resPath.vehClass.header())
        body = backport.text(resPath.vehClass.body(), forbiddenClass=classSubStr)
    return makeTooltip(header, body)
