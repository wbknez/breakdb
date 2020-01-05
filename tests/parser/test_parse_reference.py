"""
Contains unit tests to ensure that all functions involved in parsing DICOM
references work as intended.
"""
import pytest

from breakdb.parser import has_reference, parse_reference, get_sequence_value, \
    MissingTag, MissingSequence, MalformedSequence
from breakdb.tag import ReferenceTag
from tests.helpers.assertion import match


class TestParseReference:
    """
    Test suite for :function: 'has_reference' and :function: 'parse_reference'.
    """

    def test_has_reference_is_false_when_reference_is_missing(self,
                                                              create_dataset):
        ds = create_dataset(excludes=[ReferenceTag.SEQUENCE])

        assert not has_reference(ds)

    def test_has_reference_is_false_when_no_references_exist(self,
                                                             create_dataset):
        ds = create_dataset()

        del ds[ReferenceTag.SEQUENCE.value].value[0]

        assert not has_reference(ds)

    def test_has_reference_is_true_when_reference_is_present(self,
                                                             create_dataset):
        ds = create_dataset()

        assert has_reference(ds)

    def test_parse_reference_succeeds(self, create_dataset):
        ds = create_dataset()

        seq = get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)
        obj = get_sequence_value(seq, 0, ReferenceTag.OBJECT)

        parsed = parse_reference(ds)

        match(obj, parsed["ref"], ReferenceTag.SOP_CLASS)
        match(obj, parsed["ref"], ReferenceTag.SOP_INSTANCE)
        match(seq, parsed["ref"], ReferenceTag.SERIES)

    def test_parse_reference_throws_when_sequence_is_missing(self,
                                                             create_dataset):
        ds = create_dataset()

        del ds[ReferenceTag.SEQUENCE.value]

        with pytest.raises(MissingSequence):
            parse_reference(ds)

    def test_parse_reference_throws_when_object_is_missing(self,
                                                           create_dataset):
        ds = create_dataset()

        del ds[ReferenceTag.SEQUENCE.value].value[0]

        with pytest.raises(MalformedSequence):
            parse_reference(ds)

    def test_parse_reference_throws_when_class_is_missing(self,
                                                          create_dataset):
        ds = create_dataset()

        seq = get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)
        obj = get_sequence_value(seq, 0, ReferenceTag.OBJECT)

        del obj[ReferenceTag.SOP_CLASS.value]

        with pytest.raises(MissingTag):
            parse_reference(ds)

    def test_parse_reference_throws_when_instance_is_missing(self,
                                                             create_dataset):
        ds = create_dataset()

        seq = get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)
        obj = get_sequence_value(seq, 0, ReferenceTag.OBJECT)

        del obj[ReferenceTag.SOP_INSTANCE.value]

        with pytest.raises(MissingTag):
            parse_reference(ds)

    def test_parse_reference_throws_when_series_is_missing(self,
                                                           create_dataset):
        ds = create_dataset()

        seq = get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)

        del seq[ReferenceTag.SERIES.value]

        with pytest.raises(MissingTag):
            parse_reference(ds)
