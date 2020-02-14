"""
Contains unit tests to ensure that all functions involved in parsing
windowing DICOM tags work as intended.
"""
import pytest

from breakdb.parse import has_windowing, parse_windowing
from breakdb.tag import WindowingTag, MissingTag
from tests.helpers.tag import match


class TestParseWindowing:
    """
    Test suite for :function: 'parse_windowing'.
    """

    def test_has_windowing_is_false_when_center_is_not_present(self,
                                                               create_dataset):
        ds = create_dataset(excludes=[WindowingTag.CENTER])

        assert not has_windowing(ds)

    def test_has_windowing_is_false_when_width_is_not_present(self,
                                                              create_dataset):
        ds = create_dataset(excludes=[WindowingTag.WIDTH])

        assert not has_windowing(ds)

    def test_has_windowing_succeeds(self, create_dataset):
        ds = create_dataset()

        assert has_windowing(ds)

    def test_parse_windowing_throws_when_center_is_missing(self,
                                                           create_dataset):
        ds = create_dataset(excludes=[WindowingTag.CENTER])

        with pytest.raises(MissingTag):
            parse_windowing(ds)

    def test_parse_windowing_throws_when_width_is_missing(self,
                                                          create_dataset):
        ds = create_dataset(excludes=[WindowingTag.WIDTH])

        with pytest.raises(MissingTag):
            parse_windowing(ds)

    def test_parse_windowing_succeeds(self, create_dataset):
        ds = create_dataset()

        parsed = parse_windowing(ds)

        match(ds, parsed, WindowingTag.CENTER)
        match(ds, parsed, WindowingTag.WIDTH)