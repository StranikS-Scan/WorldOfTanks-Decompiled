# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/helpers_common.py
DEVICE_SLOWED_REPAIR_MASK = 128

def packDeviceRepairProgress(progress, isSlowedRepair):
    return progress | DEVICE_SLOWED_REPAIR_MASK if isSlowedRepair else progress


def unpackDeviceRepairProgress(progressData):
    return (progressData & ~DEVICE_SLOWED_REPAIR_MASK, bool(progressData & DEVICE_SLOWED_REPAIR_MASK))
