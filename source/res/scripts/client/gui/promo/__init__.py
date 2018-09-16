# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/promo/__init__.py
from skeletons.gui.shared.promo import IPromoLogger
__all__ = ('getPromoConfig',)

def getPromoConfig(manager):
    from gui.promo.promo_logger import PromoLogger
    logger = PromoLogger()
    manager.addInstance(IPromoLogger, logger, finalizer='fini')
