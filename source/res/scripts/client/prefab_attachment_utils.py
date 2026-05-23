# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/prefab_attachment_utils.py
import CGF
from constants import IS_UE_EDITOR
from gui import g_tankActiveCamouflage
from helpers import isPlayerAvatar
from PrefabsLoading import PrefabDataListLoader
from cgf_components.prefab_attachment_component import PrefabAttachmentsLoader, PrefabAttachmentComponent
from items.components.c11n_constants import SeasonType

class ModelTypesList(object):
    HANGAR = 0
    DEFAULT = 1


MODEL_TYPES_LIST = {ModelTypesList.HANGAR: 'Hangar',
 ModelTypesList.DEFAULT: 'Default'}

def getCurrentPrefabModelName(attachment):
    if isPlayerAvatar() and attachment.modelName:
        return attachment.modelName
    return attachment.hangarModelName if attachment.hangarModelName else ''


def getPrefabAttachments(appearance, typeDescriptor):
    prefabs = []
    if IS_UE_EDITOR:
        showModelsOfType = typeDescriptor.type.edModelsSets.source['default'].showModelsOfType
        if showModelsOfType == ModelTypesList.HANGAR:
            prefabs = [ attachment.hangarModelName for attachment in typeDescriptor.type.prefabAttachments if attachment.hangarModelName ]
        elif showModelsOfType == ModelTypesList.DEFAULT:
            prefabs = [ attachment.modelName for attachment in typeDescriptor.type.prefabAttachments if attachment.modelName ]
    else:
        style = appearance.outfit.style
        season = g_tankActiveCamouflage.get(typeDescriptor.type.compactDescr, SeasonType.SUMMER)
        if style is None or season is SeasonType.UNDEFINED or not style.outfits[season].overrideDefaultAttachments:
            for attachment in typeDescriptor.type.prefabAttachments:
                curPrefab = getCurrentPrefabModelName(attachment)
                if curPrefab:
                    prefabs.append(curPrefab)

    return prefabs


def addPrefabAttachments(appearance, typeDescriptor, force=False):
    prefabsToLoad = getPrefabAttachments(appearance, typeDescriptor)
    if appearance.findComponentByType(PrefabAttachmentsLoader):
        if force:
            hm = CGF.HierarchyManager(appearance.spaceID)
            childPrefabAttachments = hm.findComponentsInHierarchy(appearance.gameObject, PrefabAttachmentComponent)
            for childGO, _ in childPrefabAttachments:
                CGF.removeGameObject(childGO)

            appearance.removeComponentByType(PrefabAttachmentsLoader)
            appearance.createComponent(PrefabAttachmentsLoader, appearance, prefabsToLoad)
    else:
        appearance.createComponent(PrefabAttachmentsLoader, appearance, prefabsToLoad)


def getPrefabAttachmentsPrereqs(appearance, typeDescriptor):
    prefabs = getPrefabAttachments(appearance, typeDescriptor)
    return PrefabDataListLoader('DefaultPrefabAttachments', prefabs)
