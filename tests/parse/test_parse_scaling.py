"""
Contains unit tests to ensure that all functions involved in parsing
scaling DICOM tags work as intended.
"""
import pytest

from breakdb.parse import has_scaling, parse_scaling
from breakdb.tag import ScalingTag, MissingTag
from tests.helpers.assertion import match


class TestParseScaling:
    """
    Test suite for :function: 'parse_scaling'.
    """

    def test_has_scaling_is_false_when_intercept_is_not_present(self,
                                                                create_dataset):
        ds = create_dataset(excludes=[ScalingTag.INTERCEPT])

        assert not has_scaling(ds)

    def test_has_scaling_is_false_when_slope_is_not_present(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[ScalingTag.SLOPE])

        assert not has_scaling(ds)

    def test_has_scaling_is_false_when_type_is_not_present(self,
                                                           create_dataset):
        ds = create_dataset(excludes=[ScalingTag.TYPE])

        assert not has_scaling(ds)

    def test_has_scaling_succeeds(self, create_dataset):
        ds = create_dataset()

        assert has_scaling(ds)

    def test_parse_scaling_throws_when_intercept_is_missing(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[ScalingTag.INTERCEPT])

        with pytest.raises(MissingTag):
            parse_scaling(ds)

    def test_parse_scaling_throws_when_slope_is_missing(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[ScalingTag.SLOPE])

        with pytest.raises(MissingTag):
            parse_scaling(ds)

    def test_parse_scaling_throws_when_type_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[ScalingTag.TYPE])

        with pytest.raises(MissingTag):
            parse_scaling(ds)

    def test_parse_scaling_succeeds(self, create_dataset):
        ds = create_dataset()

        parsed = parse_scaling(ds)

        match(ds, parsed, ScalingTag.INTERCEPT)
        match(ds, parsed, ScalingTag.SLOPE)
        match(ds, parsed, ScalingTag.TYPE)
