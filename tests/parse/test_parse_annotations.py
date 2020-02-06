"""
Contains unit tests to ensure that all functions involved in parsing DICOM
references work as intended.
"""
import numpy as np
import pytest
from pydicom import Dataset

from breakdb.parse import has_annotations, has_annotation, \
    parse_annotation, parse_annotations
from breakdb.tag import AnnotationTag, get_tag, get_tag_at, \
    MissingTag, MissingSequence

class TestParseAnnotations:
    """
    Test suite for :function: 'has_annotation' and :function:
    'has_annotations' and :function: 'parse_annotation' and :function:
    'parse_annotations'.
    """

    def test_has_annotation_succeeds(self, create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        assert has_annotation(obj)

    def test_has_annotations_is_false_when_none_are_present(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[AnnotationTag.SEQUENCE])

        assert not has_annotations(ds)

    def test_has_annotations_succeeds(self, create_dataset):
        ds = create_dataset(annotations=1)

        assert has_annotations(ds)

    def test_parse_annotation_throws_when_data_is_missing(self):
        ds = Dataset()

        with pytest.raises(MissingTag):
            parse_annotation(ds)

    def test_parse_annotation_succeeds(self, create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        annots = [int(x) for x in get_tag(obj, AnnotationTag.DATA).value]
        parsed = parse_annotation(obj)

        assert len(parsed) == len(annots)
        assert parsed == annots

    def test_parse_annotations_throws_when_no_annotation_is_present(self,
                                                                create_dataset):
        ds = create_dataset(excludes=[AnnotationTag.SEQUENCE])

        with pytest.raises(MissingSequence):
            parse_annotations(ds)

    def test_parse_annotations_throws_when_annotation_is_empty(self,
                                                               create_dataset):
        ds = create_dataset(annotations=0)

        with pytest.raises(MissingTag):
            parse_annotations(ds)

    def test_parse_annotations_succeeds_with_single_annotation(self,
                                                               create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        ds_annots = [int(x) for x in get_tag(obj, AnnotationTag.DATA)]
        parsed = parse_annotations(ds)
        parsed_annots = get_tag(parsed, AnnotationTag.SEQUENCE)

        assert len(parsed_annots) == 1
        assert parsed_annots[0] == ds_annots

    def test_parse_annotations_succeeds_with_many_annotation(self,
                                                             create_dataset):
        n = np.random.randint(2, 20)
        ds = create_dataset(annotations=n)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        parsed = parse_annotations(ds)
        parsed_annots = get_tag(parsed, AnnotationTag.SEQUENCE)

        assert len(parsed_annots) == n

        for index, annot in enumerate(parsed_annots):
            obj = get_tag_at(seq, index, AnnotationTag.OBJECT)
            ds_annots = [int(x) for x in get_tag(obj, AnnotationTag.DATA)]

            assert parsed_annots[index] == ds_annots
