# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_gui_controller.py
import typing
from gui.prb_control.entities.listener import IPrbListener
from gui.hangar_presets.obsolete.hangar_gui_sf_controller import HangarGuiScaleformController
from gui.hangar_presets.sub_systems.hangar_gui_dynamic_economics import HangarGuiDynamicEconomics
from gui.hangar_presets.sub_systems.hangar_gui_providers_holder import HangarGuiProvidersHolder
from skeletons.gui.game_control import IHangarGuiController
if typing.TYPE_CHECKING:
    from gui.hangar_presets.providers.base_dynamic_gui_provider import IHangarDynamicGuiProvider

class HangarGuiController(IHangarGuiController, IPrbListener):

    def __init__(self):
        self.__providersHolder = HangarGuiProvidersHolder()
        self.__dynamicEconomics = HangarGuiDynamicEconomics(self.__providersHolder)
        self.__sfController = HangarGuiScaleformController(self.__providersHolder)

    @property
    def currentGuiProvider(self):
        return self.__providersHolder.getCurrentGuiProvider()

    @property
    def dynamicEconomics(self):
        return self.__dynamicEconomics

    @property
    def sfController(self):
        return self.__sfController

    def init(self):
        for subSystem in self.__getSubSystems():
            subSystem.init()

    def fini(self):
        for subSystem in reversed(self.__getSubSystems()):
            subSystem.fini()

    def __getSubSystems(self):
        return (self.__providersHolder, self.__dynamicEconomics, self.__sfController)
