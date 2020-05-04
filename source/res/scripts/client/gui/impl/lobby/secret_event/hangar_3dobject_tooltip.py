# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/hangar_3dobject_tooltip.py
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.hangar_object_tooltip_model import HangarObjectTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.tooltips import ToolTipBaseData
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from constants import EventHangarEnvironmentName

class Hangar3DObjectTooltip(ViewImpl):
    __slots__ = ('__title', '__image', '__description', '__tooltipType')

    def __init__(self, title, image, description, tooltipType):
        settings = ViewSettings(R.views.lobby.secretEvent.HangarObjectTooltip())
        settings.model = HangarObjectTooltipModel()
        super(Hangar3DObjectTooltip, self).__init__(settings)
        self.__title = title
        self.__image = image
        self.__description = description
        self.__tooltipType = tooltipType

    @property
    def viewModel(self):
        return super(Hangar3DObjectTooltip, self).getViewModel()

    def _onLoading(self):
        super(Hangar3DObjectTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setTitle(self.__title)
            model.setDescription(self.__description)
            model.setImage(self.__image)
            model.setType(self.__tooltipType)


class Hangar3DObjectTooltipData(ToolTipBaseData):
    _PHASE_2 = 'phase2'
    _HANGARS_PHASE_2 = (EventHangarEnvironmentName.RANDOM_PHASE_2.value, EventHangarEnvironmentName.EVENT_PHASE_2.value)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(Hangar3DObjectTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.SECRET_EVENT_HANGAR_OBJECT)

    def getDisplayableData(self, itemId, isEventHangar):
        tooltipType = HangarObjectTooltipModel.ONE if not isEventHangar else HangarObjectTooltipModel.THREE
        title, desc = self._getTitleAndDecription(itemId, isEventHangar)
        return DecoratedTooltipWindow(Hangar3DObjectTooltip(title, R.images.gui.maps.icons.secretEvent.tooltip.dyn(itemId)(), desc, tooltipType), useDecorator=False)

    def _getTitleAndDecription(self, itemId, isEventHangar):
        configName = 'eventHangar' if isEventHangar else 'randomHangar'
        environmentId = self.eventsCache.getGameEventData()['hangarEnvironmentSettings'][configName]['environmentId']
        isPhase2 = environmentId in self._HANGARS_PHASE_2
        root = R.strings.tooltips.secret_event.hangar.interactiveObject.dyn(itemId)
        if isPhase2 and self._PHASE_2 in root.keys():
            root = root.dyn(self._PHASE_2)
        return (root.title(), root.desc())
