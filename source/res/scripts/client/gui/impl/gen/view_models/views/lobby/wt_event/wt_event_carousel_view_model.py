# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_carousel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.carousel_tank_model import CarouselTankModel
from gui.impl.gen.view_models.views.lobby.wt_event.carousel_tank_status_model import CarouselTankStatusModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_consumable_slot_model import WtConsumableSlotModel

class WtEventCarouselViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(WtEventCarouselViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tanks(self):
        return self._getViewModel(0)

    @property
    def status(self):
        return self._getViewModel(1)

    @property
    def shells(self):
        return self._getViewModel(2)

    @property
    def consumables(self):
        return self._getViewModel(3)

    def _initialize(self):
        super(WtEventCarouselViewModel, self)._initialize()
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('status', CarouselTankStatusModel())
        self._addViewModelProperty('shells', UserListModel())
        self._addViewModelProperty('consumables', UserListModel())
        self.onClick = self._addCommand('onClick')
