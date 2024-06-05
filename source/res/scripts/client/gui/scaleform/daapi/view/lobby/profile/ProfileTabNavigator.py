# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTabNavigator.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection
from gui.Scaleform.daapi.view.meta.ProfileTabNavigatorMeta import ProfileTabNavigatorMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.lobby.achievements.achievements_main_view import AchievementsViewCtx
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE

class ProfileTabNavigator(ProfileTabNavigatorMeta):
    gf_views_map = [VIEW_ALIAS.PROFILE_TOTAL_PAGE, VIEW_ALIAS.PROFILE_ACHIEVEMENTS_PAGE]

    def __init__(self, *args):
        ProfileTabNavigatorMeta.__init__(self)
        self.__userName = args[0]
        self.__userID = args[1]
        self.__databaseID = args[2]
        self.__navigatorOwnInitInfo = args[3]
        self.__selectedData = None
        if len(args) > 4 and args[4]:
            self.__selectedData = args[4]
        self.tabId = None
        return

    def invokeUpdate(self):
        for component in self.components.itervalues():
            if isinstance(component, ProfileSection):
                component.invokeUpdate()

    def _populate(self):
        super(ProfileTabNavigator, self)._populate()
        self.as_setInitDataS(self.__navigatorOwnInitInfo)

    def registerFlashComponent(self, component, alias, *args):
        super(ProfileTabNavigator, self).registerFlashComponent(component, alias, self.__userName, self.__userID, self.__databaseID, self.__selectedData)

    def onTabChange(self, tabId):
        self.__safeCall(self.components.get(self.tabId), 'onSectionDeactivated')
        self.tabId = tabId
        self.__safeCall(self.components.get(self.tabId), 'onSectionActivated')

    def onViewReady(self, alias):
        if alias in self.gf_views_map:
            closeCallback = self.__selectedData.get('closeCallback') if self.__selectedData else None
            g_eventBus.handleEvent(events.Achievements20Event(events.Achievements20Event.CHANGE_GF_VIEW, ctx=AchievementsViewCtx(menuName=alias, userID=self.__userID, closeCallback=closeCallback)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @staticmethod
    def __safeCall(obj, attrName, *args, **kwargs):
        return getattr(obj, attrName, lambda *__, **_: None)(*args, **kwargs)
