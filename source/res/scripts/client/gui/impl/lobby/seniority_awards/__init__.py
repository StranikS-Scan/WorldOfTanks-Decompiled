# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/__init__.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications import GFNotificationTemplates
from gui.impl.lobby.seniority_awards.notifications.available_tokens_notification import AvailableTokensNotification
from gui.impl.lobby.seniority_awards.notifications.manual_claim_notification import ManualClaimNotification
from gui.impl.lobby.seniority_awards.notifications.vehicle_selection_notification import VehicleSelectionNotification
from gui.shared.system_factory import registerGamefaceNotifications
registerGamefaceNotifications({GFNotificationTemplates.SENIORITY_AWARD_TOKENS_NOTIFICATION: (R.views.mono.seniority_awards.notifications.tokens(), AvailableTokensNotification),
 GFNotificationTemplates.SENIORITY_AWARD_VEHICLE_SELECTION_NOTIFICATION: (R.views.mono.seniority_awards.notifications.vehicles(), VehicleSelectionNotification),
 GFNotificationTemplates.SENIORITY_AWARD_MANUAL_CLAIM_NOTIFICATION: (R.views.mono.seniority_awards.notifications.manual_claim(), ManualClaimNotification)})
