"""
Contains helper functions related to creating randomized datasets for testing.
"""
import string
from functools import partial

import numpy as np
import pytest
from pydicom import Dataset, Sequence
from pydicom.uid import generate_uid, PYDICOM_ROOT_UID


def _create_random_string(n=20):
    """
    Creates a string of the specified length consisting of random ASCII
    characters and digits.

    :param n: The length of the string to create.
    :return: A random string of ASCII characters and numbers.
    """
    choices = list(string.ascii_letters + string.digits)
    return ''.join(np.random.choice(choices) for _ in range(n))


@pytest.fixture(scope="function")
def create_dataset():
    """
    Returns a factory function to a DICOM dataset full of randomized data
    values for all possible expected tags.

    :return: A factory function to create a random DICOM dataset.
    """
    def create_annotation():
        ds = Dataset()
        xs = np.random.randint(1, 2000, 2)
        ys = np.random.randint(1, 2000, 2)

        ds.GraphicAnnotationUnits = 'PIXEL'
        ds.GraphicDimensions = 2
        ds.NumberOfGraphicPoints = 5
        ds.GraphicData = [xs[0], ys[0], xs[1], ys[0], xs[1], ys[1], xs[0],
                          ys[1], xs[0], ys[0]]
        ds.GraphicType = "POLYLINE"

        return ds

    def create_annotations(n=1):
        ds = Dataset()

        ds.GraphicLayer = "DRAW"
        ds.GraphicObjectSequence = Sequence([
            create_annotation() for _ in range(n)
        ])

        return ds

    def create_reference(uid):
        ds = Dataset()

        ds.ReferencedSOPClassUID = uid()
        ds.ReferencedSOPInstanceUID = uid()

        return ds

    def create_reference_sequence(uid):
        ds = Dataset()

        ds.ReferencedImageSequence = Sequence([
            create_reference(uid)
        ])
        ds.SeriesInstanceUID = uid()

        return ds

    def create_dataset_impl(prefix=PYDICOM_ROOT_UID, n=20, excludes=None,
                            annotations=1):
        """
        Create a DICOM dataset with randomized values for all possible
        project-specific tags.

        :param prefix: The DICOM UUID prefix to use.
        :param n: The maximum number of characters to use for any randomized
        string(s).
        :param excludes: The collection of top-level tags to exclude from creation.
        :return: A random DICOM dataset.
        """
        ds = Dataset()
        uid = partial(generate_uid, prefix=prefix)

        ds.SOPClassUID = uid()
        ds.SOPInstanceUID = uid()
        ds.SeriesInstanceUID = uid()

        ds.GraphicAnnotationSequence = Sequence([
            create_annotations(annotations)
        ])
        ds.ReferencedSeriesSequence = Sequence([
            create_reference_sequence(uid)
        ])

        ds.Columns = np.random.randint(1, 2000)
        ds.Rows = np.random.randint(1, 2000)
        ds.Pixels = np.zeros((ds.Rows, ds.Columns))

        ds.BodyPart = _create_random_string(np.random.randint(1, n))

        if excludes:
            for exclude in excludes:
                del ds[exclude.value]

        return ds

    return create_dataset_impl
