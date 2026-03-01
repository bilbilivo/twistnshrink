"""Shared test fixtures for TwistnShrink tests."""

import io

import piexif
import pytest
from PIL import Image


@pytest.fixture
def sample_image():
    """Create a simple 200x100 RGB test image with no EXIF data."""
    return Image.new("RGB", (200, 100), color="red")


@pytest.fixture
def sample_image_with_exif():
    """Create a 200x100 RGB test image with EXIF data including an orientation tag."""
    img = Image.new("RGB", (200, 100), color="blue")

    # Build EXIF data with an orientation tag (value 6 = rotated 90 CW)
    exif_dict = {"0th": {piexif.ImageIFD.Orientation: 6}}
    exif_bytes = piexif.dump(exif_dict)

    # Save to buffer with EXIF, then re-open so img.info["exif"] is populated
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif_bytes)
    buf.seek(0)
    return Image.open(buf)



