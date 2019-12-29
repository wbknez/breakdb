"""
Contains classes and functions related to working with DICOM tags and metadata.
"""
from enum import Enum, unique

from pydicom.tag import Tag


@unique
class PointTags(Enum):
    """
    Represents a collection of DICOM tags that specify the geometry of an
    annotation.
    """

    Count = Tag(0x0070, 0x0021)
    """
    Represents the number of individual points that comprise a geometry.
    
    For this project, this should always be "5".
    """

    Data = Tag(0x0070, 0x0022)
    """
    Represents the individual points as a pair of two-dimensional coordinates 
    that comprise a geometry.    
    """

    Dimensions = Tag(0x0070, 0x0020)
    """
    Represents the planar dimensions (one dimensional, two dimensional, 
    etc.).
    
    For this project, this should always be "2".
    """

    Type = Tag(0x0070, 0x0023)
    """
    Represents the type of geometry.
    
    For this project, this should always be "POLYLINE".    
    """
