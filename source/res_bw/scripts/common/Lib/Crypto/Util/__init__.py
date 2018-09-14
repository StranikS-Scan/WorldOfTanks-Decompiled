# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Util/__init__.py
"""Miscellaneous modules

Contains useful modules that don't belong into any of the
other Crypto.* subpackages.

========================    =============================================
Module                      Description
========================    =============================================
`Crypto.Util.number`        Number-theoretic functions (primality testing, etc.)
`Crypto.Util.Counter`       Fast counter functions for CTR cipher modes.
`Crypto.Util.randpool`      Random number generation
`Crypto.Util.RFC1751`       Converts between 128-bit keys and human-readable
                            strings of words.
`Crypto.Util.asn1`          Minimal support for ASN.1 DER encoding
`Crypto.Util.Padding`       Set of functions for adding and removing padding.
========================    =============================================

"""
__all__ = ['number',
 'strxor',
 'Counter',
 'galois',
 'cpuid']
__revision__ = '$Id$'
