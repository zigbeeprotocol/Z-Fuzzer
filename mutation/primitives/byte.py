import struct

import six

from .bit_field import BitField


class Byte(BitField):
    def __init__(self, value, *args, **kwargs):
        # Inject the one parameter we care to pass in (width)
        width = 8
        max_num = None

        super(Byte, self).__init__(value, width, max_num, *args, **kwargs)

        if not isinstance(self._value, (six.integer_types, list, tuple)):
            self._value = struct.unpack(self.endian + "B", self._value)[0]
