# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/pack_items_popover.py
from gui.Scaleform.daapi.view.meta.PackItemsPopoverMeta import PackItemsPopoverMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.utils import flashObject2Dict
from helpers.i18n import makeString

class PackItemsPopover(PackItemsPopoverMeta):

    def __init__(self, ctx=None):
        super(PackItemsPopover, self).__init__(ctx)
        self.__rawData = ctx.get('data')

    def _populate(self):
        super(PackItemsPopover, self)._populate()
        pack = flashObject2Dict(self.__rawData)
        title = '{}\n{}'.format(text_styles.highTitle(pack.get('title', TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_TITLE)), text_styles.main(makeString(pack.get('desc', TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_DESC), count=pack.get('count'))))
        items = []
        for item in pack.get('items'):
            item = flashObject2Dict(item)
            items.append({'value': item.get('count'),
             'icon': item.get('icon'),
             'description': item.get('desc'),
             'hasCompensation': item.get('hasCompensation', False)})

        self.as_setItemsS(title, items)

    def _dispose(self):
        self.__rawData = None
        super(PackItemsPopover, self)._dispose()
        return
