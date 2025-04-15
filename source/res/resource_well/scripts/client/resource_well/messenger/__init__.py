# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/messenger/__init__.py
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from gui.shared.system_factory import registerMessengerServerFormatter
from resource_well.messenger.formatters.service_channel import ResourceWellRewardFormatter, ResourceWellNoVehiclesFormatter

def registerResourceWellMessengerFormatter():
    registerMessengerServerFormatter(_SM_TYPE.resourceWellReward.index(), ResourceWellRewardFormatter())
    registerMessengerServerFormatter(_SM_TYPE.resourceWellNoVehicles.index(), ResourceWellNoVehiclesFormatter())
