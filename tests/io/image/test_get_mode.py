"""
Contains unit tests that ensure that the conversion from DICOM photometric
interpretation to PIL image mode(s) works correctly.
"""
import pytest
from pydicom import Dataset

from breakdb.io.image import UnknownImageFormat, get_mode


class TestGetMode:
    """
    Test suite for :function: 'get_mode'.
    """

    def test_get_mode_succeeds(self):
        interpretations = [
            "MONOCHROME1",
            "MONOCHROME2",
            "RGB",
            "YBR_FULL"
        ]
        modes = [
            "L",
            "L",
            "RGB",
            "YCbCr"
        ]

        for interp, mode in zip(interpretations, modes):
            ds = Dataset()

            ds.PhotometricInterpretation = interp

            assert get_mode(ds) == mode

    def test_get_mode_throws_when_no_valid_mapping_exists(self):
        interpretations = [
            "ARGB",
            "CMYK",
            "HSV",
            "PALETTE COLOR",
            "YBR_FULL_422",
            "YBR_PARTIAL_422",
            "YBR_PARTIAL_420"
        ]

        for interp in interpretations:
            ds = Dataset()

            ds.PhotometricInterpretation = interp

            with pytest.raises(UnknownImageFormat):
                get_mode(ds)
