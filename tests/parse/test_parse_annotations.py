"""
Contains unit tests to ensure that all functions involved in parsing DICOM
references work as intended.
"""
import numpy as np
import pytest

from breakdb.parse import has_annotations, has_annotation, \
    parse_annotation, parse_annotations
from breakdb.tag import AnnotationTag, get_tag, get_tag_at, \
    MissingTag, MissingSequence
from tests.helpers.assertion import match


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

    def test_parse_annotation_throws_when_count_is_missing(self,
                                                           create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        del obj[AnnotationTag.COUNT.value]

        with pytest.raises(MissingTag):
            parse_annotation(obj)

    def test_parse_annotation_throws_when_data_is_missing(self,
                                                          create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        del obj[AnnotationTag.DATA.value]

        with pytest.raises(MissingTag):
            parse_annotation(obj)

    def test_parse_annotation_throws_when_dimensions_is_missing(self,
                                                                create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        del obj[AnnotationTag.DIMENSIONS.value]

        with pytest.raises(MissingTag):
            parse_annotation(obj)

    def test_parse_annotation_throws_when_type_is_missing(self,
                                                          create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        del obj[AnnotationTag.TYPE.value]

        with pytest.raises(MissingTag):
            parse_annotation(obj)

    def test_parse_annotation_throws_when_units_is_missing(self,
                                                           create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        del obj[AnnotationTag.UNITS.value]

        with pytest.raises(MissingTag):
            parse_annotation(obj)

    def test_parse_annotation_succeeds(self, create_dataset):
        ds = create_dataset(annotations=1)

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        parsed = parse_annotation(obj)

        match(obj, parsed, AnnotationTag.COUNT)
        match(obj, parsed, AnnotationTag.DATA)
        match(obj, parsed, AnnotationTag.DIMENSIONS)
        match(obj, parsed, AnnotationTag.TYPE)
        match(obj, parsed, AnnotationTag.UNITS)

    def test_parse_annotations_succeeds_with_single_annotation(self,
                                                               create_dataset):
        ds = create_dataset(annotations=1)

        parsed = parse_annotations(ds)
        annots = parsed[AnnotationTag.SEQUENCE.value]

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        obj = get_tag_at(seq, 0, AnnotationTag.OBJECT)

        assert len(annots) == 1
        match(obj, annots[0], AnnotationTag.COUNT)
        match(obj, annots[0], AnnotationTag.DATA)
        match(obj, annots[0], AnnotationTag.DIMENSIONS)
        match(obj, annots[0], AnnotationTag.TYPE)
        match(obj, annots[0], AnnotationTag.UNITS)

    def test_parse_annotations_succeeds_with_mant_annotation(self,
                                                             create_dataset):
        n = np.random.randint(1, 20)
        ds = create_dataset(annotations=n)

        parsed = parse_annotations(ds)
        annots = parsed[AnnotationTag.SEQUENCE.value]

        seq = get_tag_at(ds, 0, AnnotationTag.SEQUENCE)
        objs = get_tag(seq, AnnotationTag.OBJECT)

        assert len(annots) == n

        for annot, obj in zip(annots, objs):
            match(obj, annot, AnnotationTag.COUNT)
            match(obj, annot, AnnotationTag.DATA)
            match(obj, annot, AnnotationTag.DIMENSIONS)
            match(obj, annot, AnnotationTag.TYPE)
            match(obj, annot, AnnotationTag.UNITS)

    def test_parse_annotations_throws_when_sequence_is_missing(self,
                                                               create_dataset):
        ds = create_dataset(excludes=[AnnotationTag.SEQUENCE])

        with pytest.raises(MissingSequence):
            parse_annotations(ds)
