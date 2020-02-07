"""
Contains unit tests to ensure that all functions involved in parsing pixel
DICOM tags work as intended.
"""
import pytest

from breakdb.parse import has_pixels, parse_pixels
from breakdb.tag import PixelTag, MissingTag
from tests.helpers.assertion import match


class TestParsePixels:
    """
    Test suite for :function: 'parse_pixels'.
    """

    def test_has_pixels_is_false_when_no_bits_alloc_is_present(self,
                                                               create_dataset):
        ds = create_dataset(excludes=[PixelTag.BITS_ALLOCATED])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_bits_stored_is_present(self,
                                                                create_dataset):
        ds = create_dataset(excludes=[PixelTag.BITS_STORED])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_columns_is_present(self,
                                                            create_dataset):
        ds = create_dataset(excludes=[PixelTag.COLUMNS])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_data_is_present(self, create_dataset):
        ds = create_dataset(excludes=[PixelTag.DATA])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_photo_interp_is_present(self,
                                                               create_dataset):
        ds = create_dataset(excludes=[PixelTag.PHOTOMETRIC_INTERPRETATION])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_representation_is_present(self,
                                                                create_dataset):
        ds = create_dataset(excludes=[PixelTag.REPRESENTATION])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_rows_is_present(self, create_dataset):
        ds = create_dataset(excludes=[PixelTag.ROWS])

        assert not has_pixels(ds)

    def test_has_pixels_is_false_when_no_samples_per_pixel_is_present(self,
                                                                create_dataset):
        ds = create_dataset(excludes=[PixelTag.SAMPLES_PER_PIXEL])

        assert not has_pixels(ds)

    def test_parse_pixels_throws_when_columns_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[PixelTag.COLUMNS])

        with pytest.raises(MissingTag):
            parse_pixels(ds)

    def test_parse_pixels_throws_when_rows_is_missing(self, create_dataset):
        ds = create_dataset(excludes=[PixelTag.ROWS])

        with pytest.raises(MissingTag):
            parse_pixels(ds)

    def test_parse_pixels_succeeds(self, create_dataset):
        ds = create_dataset()

        parsed = parse_pixels(ds)

        match(ds, parsed, PixelTag.COLUMNS)
        match(ds, parsed, PixelTag.ROWS)
