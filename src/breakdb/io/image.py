"""
Represents a collection of functions to assist with loading image data from
a collated DICOM database.
"""
import sys
from enum import Enum

import numpy as np
from PIL import Image
from pydicom import Dataset, dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut

from breakdb.tag import has_tag, WindowingTag


class ImageMode(Enum):
    """
    Represents the different types of images supported by this project.
    """

    MONOCHROME1 = "L"
    """
    Represents a grayscale image where zero is black.    
    """

    MONOCHROME2 = "L"
    """
    Represents a grayscale image where zero is one.    
    """

    RGB = "RGB"
    """
    Represents a color image where each pixel consists of a red, green, 
    and blue color.    
    """

    YBR_FULL = "YCbCr"
    """
    Represents a color image where each pixel consists of a single luminosity 
    and two chrominance values.
    """


class UnknownImageFormat(Exception):
    """
    Represents an exception that is raised whenever a matching PIL image
    mode cannot be found for a specified DICOM photometric interpretation.
    """

    def __init__(self, interp):
        super().__init__(
            f"Could not find matching PIL image mode for: {interp}."
        )


def compute_resize_ratio(width, height, target_width, target_height,
                         no_upscale):
    """
    Computes the proportional amount that would allow an image with the
    specified width and height to maintain the same aspect ratio when scaled to
    the specified alternate dimensions.

    :param width: The current image width.
    :param height: The current image height.
    :param target_width: The target image width.
    :param target_height: The target image height.
    :param no_upscale: Whether or not to disallow upscaling (i.e. results
    greater than one).
    :return: A proportional scalar for image resizing.
    """
    max_scale = 1.0 if no_upscale else sys.maxsize * 1.0

    return np.min([max_scale, target_width / width, target_height / height])


def compute_resize_dimensions(width, height, target_width, target_height,
                              preserve_aspect_ratio, no_upscale):
    """
    Computes the dimensions that should be used to resize an image with the
    specified width and height to the specified dimensions depending on
    whether or not the aspect ratio should be preserved and up-scaling is
    allowed.

    :param width: The current image width.
    :param height: The current image height.
    :param target_width: The target image width.
    :param target_height: The target image height.
    :param preserve_aspect_ratio: Whether or not to preserve the aspect
    ratio during resizing.
    :param no_upscale: Whether or not to disallow dimension upscaling.
    :return: The width and height to resize an image.
    """
    if not target_width:
        target_width = width

    if not target_height:
        target_height = height

    resize_width = target_width
    resize_height = target_height

    if preserve_aspect_ratio:
        ratio = compute_resize_ratio(width, height, target_width,
                                     target_height, no_upscale)

        resize_width = np.min([np.floor(ratio * width), target_width])
        resize_height = np.min([np.floor(ratio * height), target_height])
    else:
        if no_upscale and (target_width > width):
            resize_width = width
        if no_upscale and (target_height > height):
            resize_height = height

    return resize_width, resize_height



def format_as(attrs, arr, resize_width=None, resize_height=None,
              keep_aspect_ratio=True, no_upscale=False):
    """
    Formats the specified image data array as a Pillow image and resizes it
    to the specified dimensions as necessary.

    :param attrs: The current image attributes.
    :param arr: The array of image data.
    :param resize_width: The width to resize the image to (optional).
    :param resize_height: The height to resize the image to (optional).
    :param keep_aspect_ratio: Whether or not to ensure the aspect ratio
    stays the same during (any) resize operations.
    :param no_upscale: Whether or not to forbid upscaling.
    :return: A pillow formatted image.
    """
    arr = normalize(arr)

    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)

    image = Image.fromarray(arr, mode=attrs[2])

    if resize_width or resize_height:
        if not resize_width:
            resize_width = attrs[0]

        if not resize_height:
            resize_height = attrs[1]

        image = image.resize((resize_width, resize_height), Image.BICUBIC)

    return image


def get_mode(ds):
    """
    Returns the PIL compatible image mode associated with the photometric
    interpretation contained in the specified dataset.

    :param ds: The dataset to search.
    :return: A PIL image mode.
    :raises UnknownImageFormat:
    """
    interp = ds.PhotometricInterpretation

    try:
        return ImageMode[interp].value
    except KeyError as ke:
        raise UnknownImageFormat(interp) from ke


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


def read_from_database(index, db, coerce_to_original_data_type=False,
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
    :return: A pair containing basic image attributes as a tuple and an
    array of image pixel data.
    """
    file_path = db["File Path"][index]
    ds = Dataset()

    with dcmread(file_path) as meta:
        attrs = (meta.Columns, meta.Rows, get_mode(meta))
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

        if coerce_to_original_data_type and arr.dtype != dtype:
            arr = arr.astype(dtype)

        return attrs, arr


def transform_coordinate_collection(coord_list, width, height, new_width,
                                    new_height):
    """
    Transforms the specified collection of coordinate collections located in an
    image with the specified width and height to a new image with different
    dimensions.

    :param coord_list: The collection of coordinate collections to transform.
    :param width: The current image width.
    :param height: The current image height.
    :param new_width: The new image width.
    :param new_height: The new image height.
    :return: A collection of transformed coordinate collections.
    """
    if (width == new_width) and (height == new_height):
        return coord_list

    return [
        transform_coords(coords, width, height, new_width, new_height)
        for coords in coord_list
    ]


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
    x = np.array(coords[0::2], np.float)
    y = np.array(coords[1::2], np.float)

    x_t = x * (new_width / width)
    y_t = y * (new_height / height)

    return np.insert(y_t, np.arange(len(x_t)), x_t)
