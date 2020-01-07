"""
Contains unit tests to ensure that all functions involved in parsing common
DICOM tags work as intended.
"""
import pytest

from breakdb.parse import parse_common, MissingTag
from breakdb.tag import CommonTag
from tests.helpers.assertion import match


class TestParseCommon:
    """
    Test suite for :function: 'parse_common'.
    """

    def test_parse_common_throws_when_class_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[CommonTag.SOP_CLASS])

        with pytest.raises(MissingTag):
            parse_common(ds)

    def test_parse_common_throws_when_instance_is_missing(self,
                                                          create_dataset):
        ds = create_dataset(excludes=[CommonTag.SOP_CLASS])

        with pytest.raises(MissingTag):
            parse_common(ds)

    def test_parse_common_throws_when_series_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[CommonTag.SERIES])

        with pytest.raises(MissingTag):
            parse_common(ds)

    def test_parse_common_succeeds(self, create_dataset):
        ds = create_dataset()
        parsed = parse_common(ds)

        match(ds, parsed, CommonTag.SOP_CLASS)
        match(ds, parsed, CommonTag.SOP_INSTANCE)
        match(ds, parsed, CommonTag.SERIES)
