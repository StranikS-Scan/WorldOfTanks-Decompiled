# Embedded file name: scripts/client/helpers/drr_scale.py
import BigWorld
DRR_MIN_SCALE_VALUE = 0.6
DRR_MAX_SCALE_VALUE = 1.0
DRR_MAX_STEP_VALUE = 0.05
PERCENT_MODIFIER = 100.0

def normalizeScale(value):
    result = min(max(round(value, 2), DRR_MIN_SCALE_VALUE), DRR_MAX_SCALE_VALUE)
    modulo = result * PERCENT_MODIFIER % (DRR_MAX_STEP_VALUE * PERCENT_MODIFIER)
    if modulo:
        result = result - modulo / PERCENT_MODIFIER
    return result


def getPercent(value):
    return round(value, 3) * PERCENT_MODIFIER


def changeScaleByStep(offset):
    result = None
    scale = BigWorld.getDRRScale()
    newScale = normalizeScale(scale + offset)
    if scale != newScale:
        BigWorld.setDRRScale(newScale)
        if normalizeScale(BigWorld.getDRRScale()) == newScale:
            result = newScale
    return result


def stepUp():
    return changeScaleByStep(DRR_MAX_STEP_VALUE)


def stepDown():
    return changeScaleByStep(-DRR_MAX_STEP_VALUE)
