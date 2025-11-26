# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/sub_systems/hangar_gui_providers_holder.py
import typing
from itertools import chain
from constants import QUEUE_TYPE
from gui.prb_control.entities.listener import IPrbListener
from gui.hangar_presets.obsolete.hangar_gui_config import getHangarGuiConfig
from gui.hangar_presets.providers.base_dynamic_gui_provider import EmptyHangarDynamicGuiProvider
from gui.shared.system_factory import collectHangarPresetsReaders, collectHangarDynamicGuiProviders
from skeletons.gui.game_control import IHangarGuiController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.providers.base_dynamic_gui_provider import IHangarDynamicGuiProvider

class HangarGuiProvidersHolder(IHangarGuiController.IHangarGuiProvidersHolder, IPrbListener):
    _EMPTY_GUI_PROVIDER = EmptyHangarDynamicGuiProvider()

    def __init__(self):
        self.__dynamicGuiProviders = {}
        self.__bonusGuiProviders = {}

    def init(self):
        readers = collectHangarPresetsReaders()
        config = getHangarGuiConfig(sorted(readers, key=lambda r: not r.isDefault()))
        self.__dynamicGuiProviders = collectHangarDynamicGuiProviders(config)
        self.__bonusGuiProviders = {bonusType:bonusGuiProvider for bonusType, bonusGuiProvider in chain(*(p.createAllBonusTypes().iteritems() for p in self.__dynamicGuiProviders.itervalues()))}

    def fini(self):
        self.__bonusGuiProviders = {}
        self.__dynamicGuiProviders = {}

    def getBonusGuiProvider(self, bonusType):
        return self.__bonusGuiProviders.get(bonusType, self._EMPTY_PRESETS_GETTER)

    def getCurrentGuiProvider(self, defaultQueueType=QUEUE_TYPE.UNKNOWN):
        prbEntity = self.prbEntity
        if prbEntity is None:
            return self._EMPTY_GUI_PROVIDER
        else:
            defaultGuiProvider = self.__dynamicGuiProviders.get(defaultQueueType, self._EMPTY_GUI_PROVIDER)
            guiProvider = self.__dynamicGuiProviders.get(prbEntity.getQueueType(), defaultGuiProvider)
            return guiProvider.createByPrbEntity(prbEntity)
