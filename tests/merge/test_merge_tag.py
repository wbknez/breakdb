"""
Contains unit tests to ensure that all functions involved in merging
individual DICOM tags work as intended.
"""
import pytest

from breakdb.merge import merge_tag, TagConflict
from breakdb.parse import parse_dataset
from breakdb.tag import CommonTag, MiscTag, PixelTag, ScalingTag, WindowingTag, \
    get_tag


class TestMergeTag:
    """
    Test suite for :function: 'merge_tag'.
    """

    TAGS = [
        CommonTag.SOP_CLASS,
        CommonTag.SOP_INSTANCE,
        CommonTag.SERIES,
        CommonTag.STUDY,
        MiscTag.BODY_PART,
        PixelTag.COLUMNS,
        PixelTag.DATA,
        PixelTag.ROWS,
        ScalingTag.INTERCEPT,
        ScalingTag.SLOPE,
        ScalingTag.TYPE,
        WindowingTag.CENTER,
        WindowingTag.WIDTH
    ]

    def test_merge_tag_does_nothing_if_source_tag_missing(self,
                                                          create_dataset):
        ds = create_dataset()

        dest = parse_dataset(ds)
        src = {}

        for tag in TestMergeTag.TAGS:
            assert merge_tag(src, dest, tag) == dest

    def test_merge_tag_throws_when_src_and_dest_do_not_match(self):
        for tag in TestMergeTag.TAGS:
            dest = {tag.value: "a"}
            src = {tag.value: "b"}

            with pytest.raises(TagConflict):
                merge_tag(src, dest, tag)

    def test_merge_tag_replaces_value_when_dest_is_empty(self, create_dataset):
        for tag in filter(lambda t: t != PixelTag.DATA, TestMergeTag.TAGS):

            dest = {}
            src = parse_dataset(create_dataset())

            assert merge_tag(src, dest, tag) ==\
                {tag.value: get_tag(src, tag)}
