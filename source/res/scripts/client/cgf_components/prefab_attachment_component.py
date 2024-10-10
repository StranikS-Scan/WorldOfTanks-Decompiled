# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/prefab_attachment_component.py
import CGF
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery, autoregister
from vehicle_systems.model_assembler import loadAppearancePrefab

@registerComponent
class PrefabAttachmentsLoader(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    def __init__(self, appearance, prefabs):
        self.prefabs = prefabs
        self.appearance = appearance
        self.inited = False


@registerComponent
class PrefabAttachmentComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class PrefabAttachmentsManager(CGF.ComponentManager):

    @onAddedQuery(PrefabAttachmentsLoader)
    def onAdded(self, component):
        appearance = component.appearance
        damagedState = hasattr(appearance, 'isVehicleDestroyed') and appearance.isVehicleDestroyed or hasattr(appearance, 'damageState') and appearance.damageState.isCurrentModelDamaged
        if not component.inited and not damagedState:
            for prefab in component.prefabs:
                loadAppearancePrefab(prefab, component.appearance, self.__onLoaded)

        component.inited = True

    def __onLoaded(self, createdGO):
        createdGO.createComponent(PrefabAttachmentComponent)
