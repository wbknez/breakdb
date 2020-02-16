"""
Represents a collection of functions to assist with loading image data from
a collated DICOM database.
"""
import numpy as np
from pydicom import Dataset, dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut

from breakdb.tag import has_tag, WindowingTag


def normalize(arr, coerce_to_uint8=False):
    """
    Applies a linear normalization to the specified collection of pixels,
    forcing each to be between 0 and 255 for image serialization.

    :param arr: The collection of pixels to normalize.
    :param coerce_to_uint8: Whether or not to convert the result to a
    collection of unsigned integers instead of floating-point numbers.
    :return: A collection of normalized pixel values.
    """
    if arr.dtype != np.float:
        arr = arr.astype(np.float)

    if arr.min() != 0.0:
        arr = arr - arr.min()

    if arr.max() != 255.0 and arr.max() != 0.0:
        arr = (arr / arr.max()) * 255.0

    return arr if not coerce_to_uint8 else arr.astype(np.uint8)


def read_image_from_database(index, db, coerce_to_original_data_type=False,
                             ignore_scaling=False, ignore_windowing=False,
                             slope=None, intercept=None, center=None,
                             width=None, voi_func=None):
    """
    Attempts to read the (raw) image data from the DICOM file associated
    with the specified index in the specified DICOM database and apply any
    and all visual transformations to it.

    By default, all configurable parameters are assumed to be contained in
    the same DICOM dataset that provides the (raw) pixel array.  These
    values may be replaced with user-chosen parameters.

    Per the DICOM standard, scaling operations transform a pixel array by
    applying a linear transformation using a slope and intercept.  Windowing operations bound an original (raw) image array, forcing all
    pixel values to lie between a specific range in order to enhance or
    assist visualization of key features; such operations must always occur
    after scaling.  Due to the chance that these values are non-integers,
    the returned pixel array contains floating-point numbers instead of
    integers.

    Because the resulting (raw) pixel array may be of a different data type
    than that of the original DICOM, an option is provided to coerce the
    result back to the original.

    :param index: The index of the DICOM to use.
    :param db: The database to search.
    :param coerce_to_original_data_type: Whether or not to force the final
    pixel array to be of the same type as the original.
    :param ignore_scaling: Whether or not to ignore, or not apply,
    any applicable scaling operations.
    :param ignore_windowing: Whether or not to ignore, or not apply,
    any applicable windowing operations.
    :param slope: The rescale slope to use (optional).
    :param intercept: The rescale intercept to use (optional).
    :param center: The scaling center to use (optional).
    :param width: The scaling window width to use (optional).
    :param voi_func: The VOI LUT function to use.  This may be one of:
    "Linear", "Linear_Exact", or "Sigmoid".
    :return: An array of image data.
    """
    file_path = db["File Path"][index]
    ds = Dataset()

    with dcmread(file_path) as meta:
        arr = meta.pixel_array
        dtype = arr.dtype

        if db["Scaling"][index] and not ignore_scaling:
            ds.RescaleIntercept = meta.RescaleIntercept if not intercept else \
                intercept
            ds.RescaleSlope = meta.RescaleSlope if not slope else slope

            arr = apply_modality_lut(arr, ds)

        if db["Windowing"][index] and not ignore_windowing:
            ds.BitsAllocated = meta.BitsAllocated
            ds.BitsStored = meta.BitsStored
            ds.Columns = meta.Columns
            ds.PhotometricInterpretation = meta.PhotometricInterpretation
            ds.PixelRepresentation = meta.PixelRepresentation
            ds.Rows = meta.Rows
            ds.SamplesPerPixel = meta.SamplesPerPixel

            if voi_func:
                ds.VOILUTFunction = voi_func.upper()
            elif has_tag(meta, WindowingTag.FUNCTION):
                ds.VOILUTFunction = meta.VOILUTFunction
            else:
                ds.VOILUTFunction = "LINEAR"

            ds.WindowCenter = meta.WindowCenter if not center else center
            ds.WindowWidth = meta.WindowWidth if not width else width

            arr = apply_voi_lut(arr, ds)

        return arr if not coerce_to_original_data_type else arr.astype(dtype)


def transform_coords(coords, width, height, new_width, new_height):
    """
    Transforms the specified collection of coordinates located in an image
    with the specified width and height to a new image with different
    dimensions.

    :param coords: The collection of coordinates to transform.
    :param width: The current image width.
    :param height: The current image height.
    :param new_width: The new image width.
    :param new_height: The new image height.
    :return: A collection of transformed coordinates.
    """
    x = coords[0::2]
    y = coords[1::2]

    x_t = x * (new_width / width)
    y_t = y * (new_height / height)

    return np.insert(y_t, np.arange(len(x_t)), x_t)