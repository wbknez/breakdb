"""
Contains unit tests to ensure that annotation creation in YOLOv3 format
works as intended.
"""
import numpy as np

from breakdb.io.export.yolo import create_annotation, create_annotations


class TestCreateAnnotation:
    """
    Test suite for :function: 'create_annotation' and :function:
    'create_annotations'.
    """

    def test_create_annotation_succeeds(self):
        classification = np.random.choice([0, 1], 1)[0]
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        x_max = np.max(x)
        x_min = np.min(x)
        y_max = np.max(y)
        y_min = np.min(y)

        coords = [coord for coords in zip(x, y) for coord in coords]
        bndbox = [
            (x_max - x_min) / (2.0 * width),
            (y_max - y_min) / (2.0 * height),
            (x_max - x_min) / width,
            (y_max - y_min) / height
        ]

        expected = f"{classification} {' '.join(map(str, bndbox))}"
        annotation = create_annotation(classification, coords, width, height)

        assert annotation == expected

    def test_create_annotations_creates_blank_with_empty_coordinates(self):
        classification = np.random.choice([0, 1], 1)[0]
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        expected = ["0 0.0 0.0 0.0 0.0"]
        annotations = create_annotations(classification, [], width, height)

        assert annotations == expected

    def test_create_annotations_creates_multiple_annotations(self):
        classification = np.random.choice([0, 1], 1)[0]
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        num_annotations = np.random.randint(1, 20)
        coords = []
        expected = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            x_max = np.max(x)
            x_min = np.min(x)
            y_max = np.max(y)
            y_min = np.min(y)

            coords.append([coord for coords in zip(x, y) for coord in coords])

            bndbox = [
                (x_max - x_min) / (2.0 * width),
                (y_max - y_min) / (2.0 * height),
                (x_max - x_min) / width,
                (y_max - y_min) / height
            ]
            expected.append(f"{classification} {' '.join(map(str, bndbox))}")

        result = create_annotations(classification, coords, width, height)

        assert result == expected

