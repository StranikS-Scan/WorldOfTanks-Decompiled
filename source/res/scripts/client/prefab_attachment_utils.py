# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/prefab_attachment_utils.py
import CGF
from constants import IS_UE_EDITOR
from gui import g_tankActiveCamouflage
from helpers import isPlayerAvatar
from cgf_components.prefab_attachment_component import PrefabAttachmentsComponent, PrefabAttachmentComponent
from items.components.c11n_constants import SeasonType

class ModelTypesList(object):
    HANGAR = 0
    DEFAULT = 1


MODEL_TYPES_LIST = {ModelTypesList.HANGAR: 'Hangar',
 ModelTypesList.DEFAULT: 'Default'}

def addPrefabAttachments(appearance, typeDescriptor, force=False):
    prefabsToLoad = []
    if IS_UE_EDITOR:
        showModelsOfType = typeDescriptor.type.edModelsSets.source['default'].showModelsOfType
        if showModelsOfType == ModelTypesList.HANGAR:
            prefabsToLoad = [ attachment.hangarModelName for attachment in typeDescriptor.type.prefabAttachments ]
        elif showModelsOfType == ModelTypesList.DEFAULT:
            prefabsToLoad = [ attachment.modelName for attachment in typeDescriptor.type.prefabAttachments ]
    else:
        style = appearance.outfit.style
        season = g_tankActiveCamouflage.get(typeDescriptor.type.compactDescr, SeasonType.SUMMER)
        if style is None or season is SeasonType.UNDEFINED or not style.outfits[season].overrideDefaultAttachments:
            prefabsToLoad = [ (attachment.modelName if isPlayerAvatar() else attachment.hangarModelName) for attachment in typeDescriptor.type.prefabAttachments ]
    if appearance.findComponentByType(PrefabAttachmentsComponent):
        if force:
            hm = CGF.HierarchyManager(appearance.spaceID)
            childPrefabAttachments = hm.findComponentsInHierarchy(appearance.gameObject, PrefabAttachmentComponent)
            for childGO, _ in childPrefabAttachments:
                CGF.removeGameObject(childGO)

            appearance.removeComponentByType(PrefabAttachmentsComponent)
            appearance.createComponent(PrefabAttachmentsComponent, appearance, prefabsToLoad)
    else:
        appearance.createComponent(PrefabAttachmentsComponent, appearance, prefabsToLoad)
    return
