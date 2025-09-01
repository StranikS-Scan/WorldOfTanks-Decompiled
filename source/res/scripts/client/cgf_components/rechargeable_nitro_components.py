# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rechargeable_nitro_components.py
import CGF
import SoundGroups
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onProcessQuery, onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
from cgf_common.cgf_helpers import getParentGameObjectByComponent
if IS_CLIENT:
    from RechargeableNitroController import RechargeableNitroController
else:

    class RechargeableNitroController(object):
        pass


@registerComponent
class RechargeableNitroRTPCComponent(object):
    category = 'Sound'
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Rechargeable Nitro RTPC'
    RTPCName = ComponentProperty(type=CGFMetaTypes.STRING, value='RTPC_ext_abl_nitro_fuel', editorName='RTPC name')

    def __init__(self):
        super(RechargeableNitroRTPCComponent, self).__init__()
        self.rechargeableNitroControllerGO = None
        self.progress = -1.0
        return


@autoregister(presentInAllWorlds=True)
class RechargeableNitroMechanicManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, RechargeableNitroRTPCComponent)
    def onRechargeableNitroRTPCAdded(self, gameObject, rechargeableNitroRTPCComponent):
        rechargeableNitroRTPCComponent.rechargeableNitroControllerGO = getParentGameObjectByComponent(gameObject, RechargeableNitroController)
        self.__setRechargeableNitroRTPC(rechargeableNitroRTPCComponent)

    @onProcessQuery(RechargeableNitroRTPCComponent, period=0.2)
    def onRechargeableNitroProgressRTPCProcess(self, rechargeableNitroRTPCComponent):
        self.__setRechargeableNitroRTPC(rechargeableNitroRTPCComponent)

    @onRemovedQuery(RechargeableNitroRTPCComponent)
    def onRechargeableNitroRTPCRemoved(self, rechargeableNitroRTPCComponent):
        rechargeableNitroRTPCComponent.rechargeableNitroControllerGO = None
        self.__setRechargeableNitroRTPC(rechargeableNitroRTPCComponent)
        return

    @classmethod
    def __setRechargeableNitroRTPC(cls, rechargeableNitroRTPCComponent):
        progress = 0.0
        if rechargeableNitroRTPCComponent.rechargeableNitroControllerGO is not None:
            progress = cls.__getRechargeableNitroActiveProgress(rechargeableNitroRTPCComponent.rechargeableNitroControllerGO)
        if rechargeableNitroRTPCComponent.progress != progress:
            SoundGroups.g_instance.setGlobalRTPC(rechargeableNitroRTPCComponent.RTPCName, progress)
            rechargeableNitroRTPCComponent.progress = progress
        return

    @classmethod
    def __getRechargeableNitroActiveProgress(cls, rechargeableNitroControllerGO):
        rechargeableNitroController = rechargeableNitroControllerGO.findComponentByType(RechargeableNitroController)
        return 0.0 if not rechargeableNitroController else 100 * (1 - rechargeableNitroController.getMechanicState().progress)
