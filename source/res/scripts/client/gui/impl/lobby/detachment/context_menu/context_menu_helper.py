# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/context_menu_helper.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl.gen.view_models.views.lobby.detachment.context_menus.detachment_context_menus import DetachmentContextMenus
from gui.impl.backport.backport_context_menu import createContextMenuData

def getContextMenuData(event, itemsCache=None, detachmentCache=None):
    menuId = event.getArgument('menuId')
    if menuId == DetachmentContextMenus.RECRUIT_CARD_CONTEXT_MENU:
        return getRecruitCardContextMenuData(event, itemsCache)
    elif menuId == DetachmentContextMenus.VEHICLE_SLOT_CONTEXT_MENU:
        return getVehicleSlotContextMenuData(event)
    elif menuId == DetachmentContextMenus.DETACHMENT_CARD_CONTEXT_MENU:
        return getDetachmentCardContextMenuData(event, itemsCache, detachmentCache)
    else:
        return getInstructorCardContextMenuData(event, itemsCache, detachmentCache) if menuId == DetachmentContextMenus.INSTRUCTOR_SLOT_CONTEXT_MENU else None


def getDetachmentCardContextMenuData(event, itemsCache, detachmentCache):
    detInvId = event.getArgument('detachmentId')
    contextMenuArgs = {'detInvId': int(detInvId)}
    detachment = detachmentCache.getDetachment(detInvId)
    vehicle = itemsCache.items.getVehicle(detachment.vehInvID)
    if vehicle and vehicle.isLocked:
        return None
    else:
        return None if detachment.isInRecycleBin else createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.DETACHMENT_CARD_CONTEXT_MENU, contextMenuArgs)


def getInstructorCardContextMenuData(event, itemsCache, detachmentCache):
    detInvID = event.getArgument('detInvID')
    slotIndex = event.getArgument('slotIndex')
    contextMenuArgs = {'detInvID': int(detInvID),
     'slotIndex': int(slotIndex)}
    detachment = detachmentCache.getDetachment(detInvID)
    vehicle = itemsCache.items.getVehicle(detachment.vehInvID)
    if vehicle and vehicle.isLocked:
        return None
    else:
        return None if detachment.isInRecycleBin else createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.INSTRUCTOR_CARD_CONTEXT_MENU, contextMenuArgs)


def getRecruitCardContextMenuData(event, itemsCache):
    contextMenuArgs = {param:event.getArgument(param) for param in ('tmanInvId',)}
    recruit = itemsCache.items.getTankman(contextMenuArgs['tmanInvId'])
    vehicle = itemsCache.items.getVehicle(recruit.vehicleInvID)
    return None if vehicle and vehicle.isLocked else createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.RECRUIT_CARD_CONTEXT_MENU, contextMenuArgs)


def getVehicleSlotContextMenuData(event):
    contextMenuArgs = {param:event.getArgument(param) for param in ('slotIndex', 'detInvID')}
    return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.DETACHMENT_VEHICLE_SLOT, contextMenuArgs)
