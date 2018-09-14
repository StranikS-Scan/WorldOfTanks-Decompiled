# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/clan_profile_event.py
from gui.shared.event_bus import SharedEvent

class ClanProfileEvent(SharedEvent):
    CLOSE_CLAN_PROFILE = 'closeClanProfile'
