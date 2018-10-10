# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/menu.py
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import CustomUserCMHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import g_appLoader
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from web_client_api import WebCommandException, w2c, W2CSchema, Field

class _UserMenuSchema(W2CSchema):
    spa_id = Field(required=True, type=(int, long, basestring))
    user_name = Field(required=True, type=basestring)
    custom_items = Field(type=list, default=[])
    excluded_items = Field(type=list, default=[])


class UserMenuWebApiMixin(object):
    browserController = dependency.descriptor(IBrowserController)

    @w2c(_UserMenuSchema, 'user_menu')
    def userMenu(self, cmd, ctx):
        context = {'dbID': cmd.spa_id,
         'userName': cmd.user_name,
         'customItems': cmd.custom_items,
         'excludedItems': cmd.excluded_items}
        callback = ctx.get('callback')
        browserView = ctx.get('browser_view')
        app = g_appLoader.getApp()
        try:
            browserView.as_showContextMenuS(CONTEXT_MENU_HANDLER_TYPE.CUSTOM_USER, context)
            cmHandler = app.contextMenuManager.getCurrentHandler()
        except AttributeError as ex:
            raise WebCommandException('Failed to show context menu: %s' % ex)

        if cmHandler is not None and isinstance(cmHandler, CustomUserCMHandler):
            webBrowser = self.browserController.getBrowser(ctx.get('browser_id'))
            webBrowser.allowMouseWheel = False

            def onSelectedCallback(optionId):
                callback({'menu_type': 'user_menu',
                 'selected_item': optionId,
                 'spa_id': cmd.spa_id})
                webBrowser.allowMouseWheel = True

            cmHandler.onSelected += onSelectedCallback
        else:
            return {'menu_type': 'user_menu',
             'selected_item': None,
             'spa_id': cmd.spa_id}
        return
