"""
Represents a collection of functions to assist with loading image data from
a collated DICOM database.
"""
from pydicom import Dataset, dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut

from breakdb.tag import has_tag, WindowingTag


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
