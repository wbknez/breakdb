"""

"""


def match(a, b):
    """
    Checks whether or not the specified XML elements are equivalent by
    comparing any and all tags, texts, tails, and sub-elements as appropriate.

    :param a: An XML element to compare.
    :param b: Another XML element to compare.
    """
    assert a.tag == b.tag
    assert a.text == b.text
    assert a.tail == b.tail
    assert a.attrib == b.attrib
    assert len(a) == len(b)

    for c, d in zip(a, b):
        match(c, d)
