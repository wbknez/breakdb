"""
Contains helper functions to assert equality conditions on datasets for
testing.
"""


def match(ds, parsed, tag):
    """
    Checks whether or not the values of the specified tag in both the
    specified dataset and parsed dictionary are equivalent.

    :param ds: The dataset to use.
    :param parsed: The dictionary of parsed tags to use.
    :param tag: The tag to compare.
    :return: Whether or not the values of a tag in both a dataset and parsed
    dictionary are equal.
    """
    assert parsed[tag.value] == ds[tag.value].value
