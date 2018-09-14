# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Protocol/__init__.py
"""Cryptographic protocols

Implements various cryptographic protocols.  (Don't expect to find
network protocols here.)

Crypto.Protocol.AllOrNothing
 Transforms a message into a set of message blocks, such that the blocks
 can be recombined to get the message back.

Crypto.Protocol.Chaffing
 Takes a set of authenticated message blocks (the wheat) and adds a number
 of randomly generated blocks (the chaff).

Crypto.Protocol.KDF
 A collection of standard key derivation functions.

:undocumented: __revision__
"""
__all__ = ['AllOrNothing', 'Chaffing', 'KDF']
__revision__ = '$Id$'
