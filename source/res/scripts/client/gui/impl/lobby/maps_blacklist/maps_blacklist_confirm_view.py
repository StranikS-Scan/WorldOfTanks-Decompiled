# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_blacklist/maps_blacklist_confirm_view.py
import logging
import typing
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.select_option_content import SelectOptionContent, MapOption
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.shared.formatters import time_formatters
if typing.TYPE_CHECKING:
    from typing import List, Optional
_logger = logging.getLogger(__name__)

class MapsBlacklistDialog(DialogTemplateView):

    def __init__(self, newMap, mapsToReplace, cooldown):
        super(MapsBlacklistDialog, self).__init__()
        self.newMap = newMap
        self.mapsToReplace = mapsToReplace
        self.cooldown = cooldown
        self._selector = None
        self._confirmButton = None
        return

    def _onLoading(self, *args, **kwargs):
        newMapNameDyn = R.strings.arenas.num(self.newMap)
        newMapName = ''
        if newMapNameDyn.isValid():
            newMapName = backport.text(newMapNameDyn.name())
        else:
            _logger.warning('New map has not valid name')
        mapAmount = len(self.mapsToReplace)
        self._setTitle(mapAmount, newMapName)
        self._selector = SelectOptionContent()
        self._setContentMessage(mapAmount, newMapName)
        if mapAmount > 0:
            self._fillOptions()
            if mapAmount == 1:
                self._selector.selectedIndex = 0
        self.setSubView(Placeholder.CONTENT, self._selector)
        confirmRes = R.strings.premacc.mapsBlacklistConfim.submit()
        if mapAmount > 0:
            confirmRes = R.strings.premacc.mapsBlacklistConfim.replace()
        self._confirmButton = ConfirmButton(confirmRes, isDisabled=mapAmount > 1)
        self.addButton(self._confirmButton)
        self.addButton(CancelButton(R.strings.premacc.mapsBlacklistConfim.cancel()))
        super(MapsBlacklistDialog, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self._selector.onSelectionChanged, self._onSelectionChanged),)

    def _setTitle(self, mapAmount, mapName):
        if mapAmount == 0:
            title = backport.text(R.strings.premacc.mapsBlacklistConfim.title(), mapName=mapName)
        elif mapAmount == 1:
            title = backport.text(R.strings.premacc.mapsBlacklistReplaceOne.title())
        else:
            title = backport.text(R.strings.premacc.mapsBlacklistReplace.title())
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(title))

    def _setContentMessage(self, mapAmount, mapName):
        timeLeft = time_formatters.getTillTimeByResource(self.cooldown, R.strings.premacc.piggyBankCard.timeLeft, removeLeadingZeros=True)
        if mapAmount == 0:
            text = backport.text(R.strings.premacc.mapsBlacklistConfim.message(), cooldownTimeStr=timeLeft)
        elif mapAmount == 1:
            text = backport.text(R.strings.premacc.mapsBlacklistReplaceOne.message(), mapName=mapName, cooldownTimeStr=timeLeft)
        else:
            text = backport.text(R.strings.premacc.mapsBlacklistReplace.message(), mapName=mapName, cooldownTimeStr=timeLeft)
        self._selector.setMessage(text)

    def _fillOptions(self):
        for mapId in self.mapsToReplace:
            self._selector.addOption(MapOption(mapId))

    def _onSelectionChanged(self):
        if self._confirmButton.isDisabled:
            self._confirmButton.isDisabled = False

    def _getAdditionalData(self):
        return None if self._selector.selectedIndex == -1 else self.mapsToReplace[self._selector.selectedIndex]
