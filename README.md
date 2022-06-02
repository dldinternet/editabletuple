# editabletuple

This module provides the `editabletuple()` function for creating classes
with a fixed sequence of fields, similar to a namedtuple, except editable.

Each instance of a class created by the editabletuple function's fields can
be accessed by index et[i] or by fieldname et.name.

If you provide a validator, it will be used when new instances are created
and updated.

To install just use `python3 -m pip install editabletuple`.

Or just copy the `editabletuple.py` file which is self-contained and depends
only on the standard library.

## Example #1: no defaults; no validator

    >>> Options = editabletuple('Options', 'maxcolors shape zoom restore')
    >>> options = Options(5, 'square', 0.9, True)
    >>> options
    Options(maxcolors=5, shape='square', zoom=0.9, restore=True)
    >>> options.maxcolors = 7
    >>> options[-1] = False
    >>> options[2] -= 0.1
    >>> options
    Options(maxcolors=7, shape='square', zoom=0.8, restore=False)

## Example #2: with defaults but no validator

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

## Example #3: with defaults and a validator

If you provide a validator function, it will be called whenever an attempt
is made to set a value, whether at construction time or later by `et[i] =
value` or `et.fieldname = value`. It is passed an attribute `index` and an
attribute `value`. It should check the value and either return the value (or
an acceptable alternative value) which will be the one actually set, or
raise a `ValueError`.

    >>> def validate_rgba(index, value):
    ...     if index == 3: # alpha channel
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
    >>> assert color.green == 99
    >>> color.red = 128
    >>> assert color[2] == 0
    >>> color[2] = 240
    >>> assert color[2] == 240
    >>> color[-1] = 0.5
    >>> color
    Rgba(red=128, green=99, blue=240, alpha=0.5)
    >>> color[1] = 299
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got 299
    >>> color.blue = -65
    Traceback (most recent call last):
        ...
    ValueError: color value must be 0-255, got -65

**License: GPLv3**
