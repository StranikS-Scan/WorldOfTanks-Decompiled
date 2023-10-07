# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/crew_member_tank_change_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.shared.gui_items.Vehicle import getIconResourceName, getType44x44IconResource
from helpers import dependency, int2roman
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys

class CrewMemberTankChangeDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_vehicleCurrent', '_vehicleNew')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanId, vehicleCurrent, vehicleNew, **kwargs):
        super(CrewMemberTankChangeDialog, self).__init__(loggingKey=CrewDialogKeys.TANK_CHANGE, **kwargs)
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._vehicleCurrent = vehicleCurrent
        self._vehicleNew = vehicleNew

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        icon = getIconResourceName(self._tankman.getExtensionLessIconWithSkin())
        self.setSubView(Placeholder.ICON, IconSet(self._tankman.bigIconDynAccessorWithSkin.dyn(icon)(), None, [R.images.gui.maps.icons.tankmen.windows.lipSmall_dialogs()]))
        titleIconMargin = -24 if self._vehicleCurrent.isElite else -32
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(str(backport.text(R.strings.dialogs.crewMemberTankChange.title(), tankName=self._vehicleCurrent.descriptor.type.shortUserString)), [ImageSubstitution(self._vehicleCurrent.typeBigIconResource(), 'icon', -12, titleIconMargin, -22, titleIconMargin)]))
        contentIconMargin = -12 if self._vehicleNew.isElite else -16
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(str(backport.text(R.strings.dialogs.crewMemberTankChange.desc(), tankLevel=int2roman(self._vehicleNew.level), icon='%(icon)s', tankName=self._vehicleNew.descriptor.type.shortUserString)), [ImageSubstitution(getType44x44IconResource(self._vehicleNew.type, self._vehicleNew.isElite)(), 'icon', -11, contentIconMargin, -13, contentIconMargin)]))
        self.addButton(ConfirmButton(R.strings.dialogs.crewMemberTankChange.transfer()))
        self.addButton(CancelButton())
        super(CrewMemberTankChangeDialog, self)._onLoading(*args, **kwargs)
        return
