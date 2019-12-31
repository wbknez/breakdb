"""
Contains classes and functions related to working with DICOM tags and metadata.
"""
from enum import Enum, unique

from pydicom.tag import Tag


@unique
class GraphicTag(Enum):
    """
    Represents a collection of DICOM tags that specify the geometry of a
    single graphical annotation.
    """

    COUNT = Tag(0x0070, 0x0021)
    """
    Represents the number of individual points that comprise a geometry.
    
    For this project, this should always be "5" for an closed quadrilateral.
    """

    DATA = Tag(0x0070, 0x0022)
    """
    Represents the individual points as a pair of two-dimensional coordinates 
    that comprise a geometry.    
    """

    DIMENSIONS = Tag(0x0070, 0x0020)
    """
    Represents the planar dimensions (one dimensional, two dimensional, 
    etc.).
    
    For this project, this should always be "2".
    """

    TYPE = Tag(0x0070, 0x0023)
    """
    Represents the type of geometry.
    
    For this project, this should always be "POLYLINE".    
    """


@unique
class ImageTag(Enum):
    """
    Represents a collection of DICOM tags that specify how an image
    contained within is formatted.
    """

    COLUMNS = Tag(0x0028, 0x0011)
    """
    Represents the number of columns in an image.
    
    Please note this is not necessarily the same as the width, as the DICOM 
    standard specifies that this may be a multiple of the horizontal 
    downsampling factor.
    """

    PIXELS = Tag(0x7fe0, 0x0010)
    """
    Represents the (raw) pixel data in a single image.
    
    For purposes of this project, each DICOM may have a maximum of one image
    (buffer of pixel data) associated with it.
    """

    ROWS = Tag(0x0028, 0x0010)
    """
    Represents the number of rows in an image.
    
    Please note this is not necessarily the same as the height, as the DICOM 
    standard specifies that this may be a multiple of the vertical 
    downsampling factor.
    """


@unique
class ReferenceTag(Enum):
    """
    Represents a collection of DICOM tags that specify how one DICOM
    may reference information contained in another.
    """

    CLASS = Tag(0x0008, 0x1150)
    """
    Represents the (unique) SOP class identifier.            
    """

    INSTANCE = Tag(0x0008, 0x1155)
    """
    Represents the (unique) SOP instance identifier.
    
    This tag is unique per file.
    """

    SERIES = Tag(0x0020, 0x000e)
    """
    Represents the (unique) series identifier.
        
    This tag is unique per series.
    """