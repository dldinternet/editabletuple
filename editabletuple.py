#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This module provides the editabletuple() and editableobject() functions.

The editabletuple() function is used tor creating classes with a fixed
sequence of fields, similar to a namedtuple, except editable.

The editableobject() function creates classes very similar to those created
by editabletuple(). The essential difference is that editableobject()'s
class's instances don't support indexing or iteration, so support only
fieldname access. They also have an addtional totuple property (not needed
for editabletuple()s since tuple(et) is sufficient due to their iteration
support).

See the function docstrings for examples and more about the editabletuple
and editableobject APIs.
'''

import functools

__version__ = '1.3.1'


def editabletuple(classname, *fieldnames, defaults=None, validator=None):
    '''Returns a Class with the given classname and fieldnames whose
    attributes can be accessed by index or fieldname.

    classname is the name of the class to create: this should also be the
    name the returned class is bound to, e.g.,
    Point = editabletuple('Point', 'x y').

    fieldnames may be one or more fieldnames, e.g., 'x', 'y', 'z', or a
    single str of space-separated fieldnames, e.g., 'x y z'.

    defaults is an optional sequence of default values; if not given or if
    fewer than the number of fields, None is used as the default.

    validator is an optional function. It is called whenever an attempt is
    made to set a value, whether at construction time or later by et[i] =
    value or et.fieldname = value. It is passed an attribute name and an
    attribute value. It should check the value and either return the value
    (or an acceptable alternative value) which will be the one actually set,
    or raise a ValueError.

    Each instance of a class created by the editabletuple() function's
    fields can be accessed by index et[i] (or by slice), or by fieldname
    et.name. Although fields can be read and written, they cannot be added
    or deleted. Since instances are mutable they are not hashable, so can't
    be used in sets or as dict keys.

    If you provide a validator, it will be used when new instances are
    created and updated.

    In addition to access by name and index, editabletuples support len(),
    in, iteration (e.g., for value in et), and the comparison operators.
    They also provide an asdict property. To obtain a tuple or list simply
    use tuple(et) or list(et).

    Example #1: no defaults; no validator

    >>> Options = editabletuple('Options', 'maxcolors shape zoom restore')
    >>> options = Options(5, 'square', 0.9, True)
    >>> options
    Options(maxcolors=5, shape='square', zoom=0.9, restore=True)
    >>> options.maxcolors = 7
    >>> options[-1] = False
    >>> options[2] -= 0.1
    >>> options
    Options(maxcolors=7, shape='square', zoom=0.8, restore=False)

    Example #2: with defaults but no validator

    >>> Rgb = editabletuple('Rgb', 'red green blue', defaults=(0, 0, 0))
    >>> black = Rgb()
    >>> black
    Rgb(red=0, green=0, blue=0)
    >>> navy = Rgb(blue=128)
    >>> navy
    Rgb(red=0, green=0, blue=128)
    >>> violet = Rgb(238, 130, 238)
    >>> violet
    Rgb(red=238, green=130, blue=238)

    Example #3: with defaults and a validator — and some API examples

    >>> def validate_rgba(name, value):
    ...     if name == 'alpha':
    ...         if not (0.0 <= value <= 1.0):
    ...             return 1.0 # silently default to opaque
    ...     elif not (0 <= value <= 255):
    ...         raise ValueError(f'color value must be 0-255, got {value}')
    ...     return value # must return a valid value or raise ValueError
    >>>
    >>> Rgba = editabletuple('Rgba', 'red', 'green', 'blue', 'alpha',
    ...                      defaults=(0, 0, 0, 1.0), validator=validate_rgba)
    >>> black = Rgba()
    >>> black
    Rgba(red=0, green=0, blue=0, alpha=1.0)
    >>> seminavy = Rgba(blue=128, alpha=0.5)
    >>> seminavy
    Rgba(red=0, green=0, blue=128, alpha=0.5)
    >>> violet = Rgba(238, 130, 238, alpha=2.5) # alpha too big
    >>> violet
    Rgba(red=238, green=130, blue=238, alpha=1.0)
    >>>
    >>> color = Rgba(green=99)
    >>> color
    Rgba(red=0, green=99, blue=0, alpha=1.0)
    >>> assert color[1] == color.green == 99
    >>> color.red = 128
    >>> assert color[2] == color.blue == 0
    >>> color[2] = 240
    >>> assert color[2] == color.blue == 240
    >>> color[-1] = 0.5
    >>> assert color[-1] == color.alpha == 0.5
    >>> color
    Rgba(red=128, green=99, blue=240, alpha=0.5)
    >>> color[1] = 299
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 299
    >>> color.green = 399
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 399
    >>> color.blue = -65
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got -65
    >>> color = Rgba(green=99, blue=256)
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 256
    >>> color = Rgba(100, 200, 300)
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 300
    >>> color = Rgba(100, 200, 250, 75)
    >>> color
    Rgba(red=100, green=200, blue=250, alpha=1.0)
    >>> color[:3]
    [100, 200, 250]
    >>> color[:]
    [100, 200, 250, 1.0]
    >>> color
    Rgba(red=100, green=200, blue=250, alpha=1.0)
    >>> color[1:3] = (20, 25)
    >>> color
    Rgba(red=100, green=20, blue=25, alpha=1.0)
    >>> [component for component in color]
    [100, 20, 25, 1.0]
    >>> list(color)
    [100, 20, 25, 1.0]
    >>> tuple(color)
    (100, 20, 25, 1.0)
    >>> color.asdict
    {'red': 100, 'green': 20, 'blue': 25, 'alpha': 1.0}

    Example #4: operators

    >>> Point = editabletuple('Point', 'x y')
    >>> p = Point(3, 4)
    >>> q = Point(3, 5)
    >>> p < q
    True
    >>> q > p
    True
    >>> p == q
    False
    >>> r = Point(*p)
    >>> r == p
    True
    >>> r != p
    False
    >>> 5 in q
    True
    >>> 5 in p
    False
    >>> del p.y
    Traceback (most recent call last):
        ...
    AttributeError: __delattr__
    >>> p
    Point(x=3, y=4)
    >>> del p[0]
    Traceback (most recent call last):
        ...
    AttributeError: __delitem__
    >>> del p[1:3]
    Traceback (most recent call last):
        ...
    AttributeError: __delitem__
    >>> p
    Point(x=3, y=4)
    >>> p.z = 99
    Traceback (most recent call last):
        ...
    AttributeError: 'Point' object has no attribute 'z'
    >>> p[3] = 5
    Traceback (most recent call last):
        ...
    IndexError: list index out of range

    Example #5: subclassing

    >>> import math
    >>> class Point(editabletuple('Point', 'x y')):
    ...    def reverse(self):
    ...        self.x, self.y = self.y, self.x
    ...    @property
    ...    def reversed(self):
    ...        return self.__class__(self.y, self.x)
    ...    def distance_to(self, other=Point(0, 0)):
    ...        return math.hypot(self.x - other.x, self.y - other.y)
    >>>
    >>> p = Point(5, 12)
    >>> q = p.reversed
    >>> p != q
    True
    >>> q
    Point(x=12, y=5)
    >>> q.reverse()
    >>> q
    Point(x=5, y=12)
    >>> p == q
    True
    >>> p.distance_to()
    13.0
    >>> p.distance_to(q)
    0.0
    >>> p.distance_to(Point(8, 12))
    3.0
    '''

    def __init__(self, *args, **kwargs):
        fields = self.__class__.__slots__
        if len(args) + len(kwargs) > len(fields):
            raise TypeError(f'{self.__class__.__name__} accepts up to '
                            f'{len(fields)} args; got {len(args)}')
        for index, name in enumerate(fields):
            default = (self._defaults[index] if self._defaults is not None
                       and index < len(self._defaults) else None)
            value = args[index] if index < len(args) else default
            setattr(self, name, value) # will call _validator if present
        names = set(fields)
        for name, value in kwargs.items():
            if name not in names:
                raise TypeError(f'{self.__class__.__name__} does not have '
                                f' a {name} field')
            setattr(self, name, value) # will call _validator if present

    def asdict(self):
        return {name: getattr(self, name) for name in self.__slots__}

    def __repr__(self):
        pairs = []
        for name in self.__class__.__slots__:
            pairs.append((name, getattr(self, name)))
        kwargs = ', '.join(f'{name}={value!r}' for name, value in pairs)
        return f'{self.__class__.__name__}({kwargs})'

    def __getitem__(self, index):
        fields = self.__class__.__slots__
        if isinstance(index, slice):
            return [getattr(self, fields[i])
                    for i in range(*index.indices(len(fields)))]
        return getattr(self, fields[index])

    def __setitem__(self, index, value):
        fields = self.__class__.__slots__
        if isinstance(index, slice):
            for i, v in zip(range(*index.indices(len(fields))), value):
                self._update(fields[i], v)
        else:
            self._update(fields[index], value)

    def __delattr__(self, _name):
        raise AttributeError('__delattr__')

    def __setattr__(self, name, value):
        self._update(name, value)

    def _update(self, name, value):
        if self._validator is not None:
            value = self._validator(name, value)
        object.__setattr__(self, name, value)

    def __len__(self):
        return len(self.__class__.__slots__)

    def __contains__(self, value): # prefer explicit rather than using iter
        for name in self.__class__.__slots__:
            if getattr(self, name) == value:
                return True
        return False

    def __iter__(self): # implicitly supports tuple(obj), list(obj)
        fields = self.__class__.__slots__
        for i in range(len(fields)):
            yield getattr(self, fields[i])

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return tuple(self) == tuple(other)

    def __lt__(self, other): # total_ordering ensures we get the rest
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return tuple(self) < tuple(other)

    if len(fieldnames) == 1 and isinstance(fieldnames[0], str):
        fieldnames = fieldnames[0].split()
    attributes = dict(
        __init__=__init__, asdict=property(asdict), __repr__=__repr__,
        __getitem__=__getitem__, __setitem__=__setitem__,
        __delattr__=__delattr__, __setattr__=__setattr__,
        __contains__=__contains__, _defaults=defaults,
        _validator=staticmethod(validator), _update=_update,
        __len__=__len__, __iter__=__iter__, __eq__=__eq__, __lt__=__lt__,
        __slots__=fieldnames)
    return functools.total_ordering(type(classname, (), attributes))


def editableobject(classname, *fieldnames, defaults=None, validator=None):
    '''
    Returns a Class with the given classname and fieldnames whose
    attributes can be accessed by fieldname.

    classname is the name of the class to create: this should also be the
    name the returned class is bound to, e.g.,
    Point = editableobject('Point', 'x y').

    fieldnames may be one or more fieldnames, e.g., 'x', 'y', 'z', or a
    single str of space-separated fieldnames, e.g., 'x y z'.

    defaults is an optional sequence of default values; if not given or if
    fewer than the number of fields, None is used as the default.

    validator is an optional function. It is called whenever an attempt is
    made to set a value, whether at construction time or later by
    et.fieldname = value. It is passed an attribute name and an attribute
    value. It should check the value and either return the value (or an
    acceptable alternative value) which will be the one actually set, or
    raise a ValueError.

    Each instance of a class created by the editableobject() function's
    fields can be accessed by fieldname, eo.name. Although fields can be
    read and written, they cannot be added or deleted. Since instances are
    mutable they are not hashable, so can't be used in sets or as dict keys.

    If you provide a validator, it will be used when new instances are
    created and updated.

    In addition to access by name, editableobjects support the comparison
    operators. They also provide asdict and astuple properties.

    Example #1: no defaults; no validator

    >>> Options = editableobject('Options', 'maxcolors shape zoom restore')
    >>> options = Options(5, 'square', 0.9, True)
    >>> options
    Options(maxcolors=5, shape='square', zoom=0.9, restore=True)
    >>> options.maxcolors = 7
    >>> options.restore = False
    >>> options.zoom -= 0.1
    >>> options
    Options(maxcolors=7, shape='square', zoom=0.8, restore=False)

    Example #2: with defaults but no validator

    >>> Rgb = editableobject('Rgb', 'red green blue', defaults=(0, 0, 0))
    >>> black = Rgb()
    >>> black
    Rgb(red=0, green=0, blue=0)
    >>> navy = Rgb(blue=128)
    >>> navy
    Rgb(red=0, green=0, blue=128)
    >>> violet = Rgb(238, 130, 238)
    >>> violet
    Rgb(red=238, green=130, blue=238)

    Example #3: with defaults and a validator — and some API examples

    >>> def validate_rgba(name, value):
    ...     if name == 'alpha':
    ...         if not (0.0 <= value <= 1.0):
    ...             return 1.0 # silently default to opaque
    ...     elif not (0 <= value <= 255):
    ...         raise ValueError(f'color value must be 0-255, got {value}')
    ...     return value # must return a valid value or raise ValueError
    >>>
    >>> Rgba = editableobject('Rgba', 'red', 'green', 'blue', 'alpha',
    ...                      defaults=(0, 0, 0, 1.0), validator=validate_rgba)
    >>> black = Rgba()
    >>> black
    Rgba(red=0, green=0, blue=0, alpha=1.0)
    >>> seminavy = Rgba(blue=128, alpha=0.5)
    >>> seminavy
    Rgba(red=0, green=0, blue=128, alpha=0.5)
    >>> violet = Rgba(238, 130, 238, alpha=2.5) # alpha too big
    >>> violet
    Rgba(red=238, green=130, blue=238, alpha=1.0)
    >>>
    >>> color = Rgba(green=99)
    >>> color
    Rgba(red=0, green=99, blue=0, alpha=1.0)
    >>> color[1]
    Traceback (most recent call last):
        ...
    TypeError: 'Rgba' object is not subscriptable
    >>> assert color.green == 99
    >>> color.red = 128
    >>> assert color.blue == 0
    >>> color.blue = 240
    >>> assert color.blue == 240
    >>> color.alpha = 0.5
    >>> assert color.alpha == 0.5
    >>> color
    Rgba(red=128, green=99, blue=240, alpha=0.5)
    >>> color.red = 299
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 299
    >>> color.green = 399
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 399
    >>> color.blue = -65
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got -65
    >>> color = Rgba(green=99, blue=256)
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 256
    >>> color = Rgba(100, 200, 300)
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 300
    >>> color = Rgba(100, 200, 250, 75)
    >>> color
    Rgba(red=100, green=200, blue=250, alpha=1.0)
    >>> color[:3]
    Traceback (most recent call last):
        ...
    TypeError: 'Rgba' object is not subscriptable
    >>> color.asdict
    {'red': 100, 'green': 200, 'blue': 250, 'alpha': 1.0}
    >>> color.astuple
    (100, 200, 250, 1.0)

    Example #4: operators

    >>> Point = editableobject('Point', 'x y')
    >>> p = Point(3, 4)
    >>> q = Point(3, 5)
    >>> p < q
    True
    >>> q > p
    True
    >>> p == q
    False
    >>> r = Point(p.x, p.y)
    >>> r == p
    True
    >>> r != p
    False
    >>> 5 in q
    Traceback (most recent call last):
        ...
    TypeError: argument of type 'Point' is not iterable
    >>> del p.y
    Traceback (most recent call last):
        ...
    AttributeError: __delattr__
    >>> p
    Point(x=3, y=4)
    >>> del p[0]
    Traceback (most recent call last):
        ...
    TypeError: 'Point' object doesn't support item deletion
    >>> del p[1:3]
    Traceback (most recent call last):
        ...
    TypeError: 'Point' object does not support item deletion
    >>> p
    Point(x=3, y=4)
    >>> p.z = 99
    Traceback (most recent call last):
        ...
    AttributeError: 'Point' object has no attribute 'z'
    >>> p[3] = 5
    Traceback (most recent call last):
        ...
    TypeError: 'Point' object does not support item assignment

    Example #5: subclassing

    >>> import math
    >>> class Point(editableobject('Point', 'x y')):
    ...    def reverse(self):
    ...        self.x, self.y = self.y, self.x
    ...    @property
    ...    def reversed(self):
    ...        return self.__class__(self.y, self.x)
    ...    def distance_to(self, other=Point(0, 0)):
    ...        return math.hypot(self.x - other.x, self.y - other.y)
    >>>
    >>> p = Point(5, 12)
    >>> q = p.reversed
    >>> p != q
    True
    >>> q
    Point(x=12, y=5)
    >>> q.reverse()
    >>> q
    Point(x=5, y=12)
    >>> p == q
    True
    >>> p.distance_to()
    13.0
    >>> p.distance_to(q)
    0.0
    >>> p.distance_to(Point(8, 12))
    3.0
    '''

    def __init__(self, *args, **kwargs):
        fields = self.__class__.__slots__
        if len(args) + len(kwargs) > len(fields):
            raise TypeError(f'{self.__class__.__name__} accepts up to '
                            f'{len(fields)} args; got {len(args)}')
        for index, name in enumerate(fields):
            default = (self._defaults[index] if self._defaults is not None
                       and index < len(self._defaults) else None)
            value = args[index] if index < len(args) else default
            setattr(self, name, value) # will call _validator if present
        names = set(fields)
        for name, value in kwargs.items():
            if name not in names:
                raise TypeError(f'{self.__class__.__name__} does not have '
                                f' a {name} field')
            setattr(self, name, value) # will call _validator if present

    def asdict(self):
        return {name: getattr(self, name) for name in self.__slots__}

    def astuple(self):
        return tuple(getattr(self, name) for name in self.__slots__)

    def __repr__(self):
        pairs = []
        for name in self.__class__.__slots__:
            pairs.append((name, getattr(self, name)))
        kwargs = ', '.join(f'{name}={value!r}' for name, value in pairs)
        return f'{self.__class__.__name__}({kwargs})'

    def __delattr__(self, _name):
        raise AttributeError('__delattr__')

    def __setattr__(self, name, value):
        if self._validator is not None:
            value = self._validator(name, value)
        object.__setattr__(self, name, value)

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.astuple == other.astuple

    def __lt__(self, other): # total_ordering ensures we get the rest
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.astuple < other.astuple

    if len(fieldnames) == 1 and isinstance(fieldnames[0], str):
        fieldnames = fieldnames[0].split()
    attributes = dict(
        __init__=__init__, asdict=property(asdict),
        astuple=property(astuple), __repr__=__repr__,
        __delattr__=__delattr__, __setattr__=__setattr__,
        _defaults=defaults, _validator=staticmethod(validator),
        __eq__=__eq__, __lt__=__lt__, __slots__=fieldnames)
    return functools.total_ordering(type(classname, (), attributes))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
