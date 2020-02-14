"""
Contains unit tests to ensure that all functions involved in parsing
miscellaneous (utility) DICOM tags work as intended.
"""
import pytest

from breakdb.parse import has_misc, parse_misc
from breakdb.tag import MiscTag, MissingTag
from tests.helpers.tag import match


class TestParseMisc:
    """
    Test suite for :function: 'parse_misc'.
    """

    def test_has_misc_is_false_when_no_body_part_is_present(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[MiscTag.BODY_PART])

        assert not has_misc(ds)

    def test_misc_succeeds(self, create_dataset):
        ds = create_dataset()

        assert has_misc(ds)

    def test_parse_misc_throws_when_body_part_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[MiscTag.BODY_PART])

        with pytest.raises(MissingTag):
            parse_misc(ds)

    def test_parse_misc_succeeds(self, create_dataset):
        ds = create_dataset()

        parsed = parse_misc(ds)

        match(ds, parsed, MiscTag.BODY_PART)
