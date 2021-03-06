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

from breakdb.tag import has_tag, WindowingTag, make_tag_list, PixelTag, \
    ScalingTag


IMAGE_TAGS = make_tag_list(
    PixelTag.BITS_ALLOCATED,
    PixelTag.BITS_STORED,
    PixelTag.COLUMNS,
    PixelTag.DATA,
    PixelTag.PHOTOMETRIC_INTERPRETATION,
    PixelTag.REPRESENTATION,
    PixelTag.ROWS,
    PixelTag.SAMPLES_PER_PIXEL,
    ScalingTag.INTERCEPT,
    ScalingTag.SLOPE,
    ScalingTag.TYPE,
    WindowingTag.CENTER,
    WindowingTag.FUNCTION,
    WindowingTag.WIDTH
)


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


def compute_resize_transform(width, height, target_width, target_height,
                             resize_width, resize_height):
    """
    Computes the origin and the scaling coefficients necessary to convert a
    pair of coordinates from an image with the specified width and height to
    another with the specified alternate dimensions.

    :param width: The current image width.
    :param height: The current image height.
    :param target_width: The target image width.
    :param target_height: The target image height.
    :param resize_width: The resized original image width.
    :param resize_height: The resized original image height.
    :return: The origin (x- and y-axis) and scaling coefficients (width and
    height) as a pair of tuples.
    """
    if not target_height:
        target_height = resize_height

    if not target_width:
        target_width = resize_width

    origin_x = int((target_width - resize_width) / 2.0)
    origin_y = int((target_height - resize_height) / 2.0)
    width_ratio = resize_width / width
    height_ratio = resize_height / height

    return (origin_x, origin_y), (width_ratio, height_ratio)


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

    return np.int(resize_width), np.int(resize_height)


def format_as(attrs, arr, target_width, target_height,
              keep_aspect_ratio=True, no_upscale=False):
    """
    Formats the specified image data array as a Pillow image and resizes it
    to the specified dimensions as necessary.

    :param attrs: The current image attributes.
    :param arr: The array of image data.
    :param target_width: The maximum width to resize the image to.
    :param target_height: The maximum height to resize the image to.
    :param keep_aspect_ratio: Whether or not to ensure the aspect ratio
    stays the same during (any) resize operations.
    :param no_upscale: Whether or not to forbid upscaling.
    :return: A formatted image and computed transform as a pair.
    """
    width, height, mode = attrs

    arr = normalize(arr)
    resize_width, resize_height = compute_resize_dimensions(
        attrs[0], attrs[1], target_width, target_height, keep_aspect_ratio,
        no_upscale
    )
    transform = compute_resize_transform(attrs[0], attrs[1], target_width,
                                         target_height, resize_width,
                                         resize_height)

    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)

    image = Image.fromarray(arr, mode=mode)

    if width != resize_width or height != resize_height:
        image = image.resize((resize_width, resize_height), Image.BICUBIC)

    if transform != ((0.0, 0.0), (1.0, 1.0)):
        scaled = Image.new(mode, (target_width, target_height), 0)
        scaled.paste(image, transform[0])

        image = scaled

    return image, transform


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


def read_from_dataset(ds, coerce_to_original_data_type=False,
                      ignore_scaling=False, ignore_windowing=False,
                       slope=None, intercept=None, center=None,
                       width=None, voi_func=None):
    """
    Attempts to read the (raw) image data from the DICOM file associated
    with the specified DICOM dataset and applies any and all visual
    transformations to it.

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

    :param ds: The DICOM dataset to use.
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
    file_path = ds["File Path"]
    img = Dataset()

    with dcmread(file_path, specific_tags=IMAGE_TAGS) as meta:
        attrs = (meta.Columns, meta.Rows, get_mode(meta))
        arr = meta.pixel_array
        dtype = arr.dtype

        if ds.Scaling and not ignore_scaling:
            img.RescaleIntercept = meta.RescaleIntercept if not intercept else \
                intercept
            img.RescaleSlope = meta.RescaleSlope if not slope else slope

            arr = apply_modality_lut(arr, img)

        if ds.Windowing and not ignore_windowing:
            img.BitsAllocated = meta.BitsAllocated
            img.BitsStored = meta.BitsStored
            img.Columns = meta.Columns
            img.PhotometricInterpretation = meta.PhotometricInterpretation
            img.PixelRepresentation = meta.PixelRepresentation
            img.Rows = meta.Rows
            img.SamplesPerPixel = meta.SamplesPerPixel

            if voi_func:
                img.VOILUTFunction = voi_func.upper()
            elif has_tag(meta, WindowingTag.FUNCTION):
                img.VOILUTFunction = meta.VOILUTFunction
            else:
                img.VOILUTFunction = "LINEAR"

            img.WindowCenter = meta.WindowCenter if not center else center
            img.WindowWidth = meta.WindowWidth if not width else width

            arr = apply_voi_lut(arr, img)

        if coerce_to_original_data_type and arr.dtype != dtype:
            arr = arr.astype(dtype)

        return attrs, arr


def transform_coordinate_collection(coord_list, origin, ratios):
    """
    Transforms the specified collection of coordinate collections located in an
    image with the specified width and height to a new image with different
    dimensions.

    :param coord_list: The collection of coordinate collections to transform.
    :param origin:
    :param ratios:
    :return: A collection of transformed coordinate collections.
    """
    if (origin == (0.0, 0.0)) and (ratios == (1.0, 1.0)):
        return coord_list

    return [
        transform_coords(coords, origin, ratios)
        for coords in coord_list
    ]


def transform_coords(coords, origin, ratios):
    """
    Transforms the specified collection of coordinates located in an image
    with the specified width and height to a new image with different
    dimensions.

    :param coords: The collection of coordinates to transform.
    :param origin:
    :param ratios:
    :return: A collection of transformed coordinates.
    """
    x = np.array(coords[0::2], np.float)
    y = np.array(coords[1::2], np.float)

    x_t = x * ratios[0] + origin[0]
    y_t = y * ratios[1] + origin[1]

    return np.insert(y_t, np.arange(len(x_t)), x_t)
