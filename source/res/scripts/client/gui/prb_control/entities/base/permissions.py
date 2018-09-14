# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/permissions.py


class IPrbPermissions(object):
    """
    Base prebattle permission interface.
    """

    def canExitFromQueue(self):
        """
        Can player exit from queue
        """
        return True

    def canChangeVehicle(self):
        """
        Can player change vehicle
        """
        return True

    def canSendInvite(self):
        """
        Can player send an invite
        """
        return False

    def canCreateSquad(self):
        """
        Can player create squad
        """
        return False
