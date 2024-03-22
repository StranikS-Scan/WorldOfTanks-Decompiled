# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/common/__init__.py
from typing import NamedTuple, List, Optional
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
IconSetData = NamedTuple('IconSetData', [('iconRes', long), ('label', Optional[str]), ('imageSubstitutions', Optional[List[ImageSubstitution]])])
