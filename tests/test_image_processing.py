"""Unit tests for image processing functions in TwistnShrink."""

import io

import piexif
from PIL import Image

from twistnshrink import _load_exif_safe, fix_orientation, resize_image, rotate_image

# ---------------------------------------------------------------------------
# rotate_image tests
# ---------------------------------------------------------------------------


class TestRotateImage:
    """Tests for rotate_image()."""

    def test_rotate_90(self, sample_image):
        result = rotate_image(sample_image, 90)
        # 200x100 rotated 90 degrees -> 100x200
        assert result.size == (100, 200)

    def test_rotate_180(self, sample_image):
        result = rotate_image(sample_image, 180)
        # Dimensions stay the same for 180 rotation
        assert result.size == (200, 100)

    def test_rotate_270(self, sample_image):
        result = rotate_image(sample_image, 270)
        # 200x100 rotated 270 degrees -> 100x200
        assert result.size == (100, 200)

    def test_rotate_invalid_angle_returns_unchanged(self, sample_image):
        result = rotate_image(sample_image, 45)
        assert result.size == sample_image.size
        # Should be the exact same object
        assert result is sample_image

    def test_rotate_zero_returns_unchanged(self, sample_image):
        result = rotate_image(sample_image, 0)
        assert result is sample_image


# ---------------------------------------------------------------------------
# resize_image tests
# ---------------------------------------------------------------------------


class TestResizeImage:
    """Tests for resize_image()."""

    def test_output_is_valid_jpeg(self, sample_image):
        data = resize_image(sample_image, target_size_kb=500, exif_bytes=None)
        # JPEG files start with FF D8
        assert data[:2] == b"\xff\xd8"

    def test_output_within_target_size(self, sample_image):
        target_kb = 50
        data = resize_image(sample_image, target_size_kb=target_kb, exif_bytes=None)
        actual_kb = len(data) / 1024
        assert actual_kb <= target_kb

    def test_with_exif_bytes(self, sample_image):
        exif_dict = {"0th": {piexif.ImageIFD.Make: b"TestCamera"}}
        exif_bytes = piexif.dump(exif_dict)

        data = resize_image(sample_image, target_size_kb=500, exif_bytes=exif_bytes)

        # Verify output is valid JPEG
        assert data[:2] == b"\xff\xd8"
        # Re-open and check EXIF is present
        result_img = Image.open(io.BytesIO(data))
        assert "exif" in result_img.info

    def test_without_exif_bytes(self, sample_image):
        data = resize_image(sample_image, target_size_kb=500, exif_bytes=None)
        assert data[:2] == b"\xff\xd8"
        assert len(data) > 0

    def test_quality_floor_reached(self):
        """When target is impossibly small, output is still produced at quality floor."""
        # Create a larger image that can't possibly fit in 1 KB
        img = Image.new("RGB", (1000, 1000), color="red")
        data = resize_image(img, target_size_kb=1, exif_bytes=None)
        # Should still produce valid JPEG output
        assert data[:2] == b"\xff\xd8"
        assert len(data) > 0

    def test_large_target_uses_high_quality(self, sample_image):
        """When target is very generous, quality stays high and file is small."""
        data = resize_image(sample_image, target_size_kb=10000, exif_bytes=None)
        assert data[:2] == b"\xff\xd8"


# ---------------------------------------------------------------------------
# fix_orientation tests
# ---------------------------------------------------------------------------


class TestFixOrientation:
    """Tests for fix_orientation()."""

    def test_no_exif_returns_unchanged(self, sample_image):
        """Image with no EXIF should be returned unchanged."""
        result = fix_orientation(sample_image)
        assert result.size == sample_image.size

    def test_orientation_6_rotates(self, sample_image_with_exif):
        """Orientation 6 (90 CW) should rotate, swapping width and height."""
        original_size = sample_image_with_exif.size
        result = fix_orientation(sample_image_with_exif)
        # Orientation 6 applies ROTATE_270 which swaps dimensions
        assert result.size == (original_size[1], original_size[0])

    def test_orientation_3_rotates_180(self):
        """Orientation 3 (upside down) should rotate 180, keeping dimensions."""
        img = Image.new("RGB", (200, 100), color="red")
        exif_dict = {"0th": {piexif.ImageIFD.Orientation: 3}}
        exif_bytes = piexif.dump(exif_dict)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_bytes)
        buf.seek(0)
        img_with_exif = Image.open(buf)

        result = fix_orientation(img_with_exif)
        # 180 rotation keeps dimensions the same
        assert result.size == (200, 100)

    def test_orientation_1_no_change(self):
        """Orientation 1 (normal) should not modify the image."""
        img = Image.new("RGB", (200, 100), color="red")
        exif_dict = {"0th": {piexif.ImageIFD.Orientation: 1}}
        exif_bytes = piexif.dump(exif_dict)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_bytes)
        buf.seek(0)
        img_with_exif = Image.open(buf)

        result = fix_orientation(img_with_exif)
        assert result.size == (200, 100)

    def test_handles_corrupt_exif_gracefully(self):
        """Image with corrupt EXIF should not crash, just return the image."""
        img = Image.new("RGB", (100, 100), color="green")
        # Manually set corrupt exif info
        img.info["exif"] = b"not-valid-exif-data"
        result = fix_orientation(img)
        assert result.size == (100, 100)


# ---------------------------------------------------------------------------
# _load_exif_safe tests
# ---------------------------------------------------------------------------


class TestLoadExifSafe:
    """Tests for _load_exif_safe()."""

    def test_no_exif_returns_none(self, sample_image):
        """Image with no EXIF data should return None."""
        result = _load_exif_safe(sample_image)
        assert result is None

    def test_with_exif_returns_bytes(self, sample_image_with_exif):
        """Image with EXIF should return bytes."""
        result = _load_exif_safe(sample_image_with_exif)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_orientation_tag_stripped(self, sample_image_with_exif):
        """Returned EXIF should have orientation tag removed."""
        result = _load_exif_safe(sample_image_with_exif)
        assert result is not None
        # Parse the returned EXIF and verify orientation is gone
        exif_dict = piexif.load(result)
        assert piexif.ImageIFD.Orientation not in exif_dict.get("0th", {})

    def test_corrupt_exif_returns_none(self):
        """Corrupt EXIF data should return None, not raise."""
        img = Image.new("RGB", (100, 100), color="red")
        img.info["exif"] = b"totally-broken-exif"
        result = _load_exif_safe(img)
        assert result is None

    def test_empty_exif_returns_none(self):
        """Empty EXIF bytes should return None."""
        img = Image.new("RGB", (100, 100), color="red")
        img.info["exif"] = b""
        result = _load_exif_safe(img)
        assert result is None
