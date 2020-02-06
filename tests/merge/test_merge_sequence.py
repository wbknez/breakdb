"""
Contains unit tests to ensure that all functions involved in merging
sequences of DICOM tags work as intended.
"""
from breakdb.merge import merge_sequence
from breakdb.parse import parse_dataset
from breakdb.tag import AnnotationTag, get_tag


class TestMergeSequence:
    """
    Test suite for :function: 'merge_sequence'.
    """

    def test_merge_tag_does_nothing_if_both_tags_are_missing(self):
        dest = {}
        src = {}

        assert merge_sequence(src, dest, AnnotationTag.SEQUENCE) == dest
        assert merge_sequence(src, dest, AnnotationTag.SEQUENCE) == {}

    def test_merge_sequence_does_nothing_if_source_tag_missing(self,
                                                               create_dataset):
        ds = create_dataset(annotations=2)

        dest = parse_dataset(ds)
        src = {}

        assert merge_sequence(src, dest, AnnotationTag.SEQUENCE) == dest

    def test_merge_tag_creates_value_when_dest_is_empty(self, create_dataset):
        ds = create_dataset(annotations=2)

        dest = {}
        src = parse_dataset(ds)

        assert merge_sequence(src, dest, AnnotationTag.SEQUENCE) == {
            AnnotationTag.SEQUENCE.value: get_tag(src, AnnotationTag.SEQUENCE)
        }

    def test_merge_tag_updates_value_when_dest_is_not_empty(self,
                                                            create_dataset):
        ds0 = create_dataset(annotations=2)
        ds1 = create_dataset(annotations=3)

        dest = parse_dataset(ds0)
        src = parse_dataset(ds1)

        result = get_tag(merge_sequence(src, dest, AnnotationTag.SEQUENCE),
                         AnnotationTag.SEQUENCE)
        expected = get_tag(dest, AnnotationTag.SEQUENCE) + \
                   get_tag(src, AnnotationTag.SEQUENCE)

        assert result == expected
