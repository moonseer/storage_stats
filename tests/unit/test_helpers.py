"""Unit tests for the helpers module."""

import pytest
from src.utils.helpers import human_readable_size, format_timestamp, get_file_icon, categorize_file_by_type


@pytest.mark.unit
class TestHumanReadableSize:
    """Tests for the human_readable_size function."""

    def test_zero_bytes(self):
        """Test that zero bytes returns '0 B'."""
        assert human_readable_size(0) == "0 B"

    def test_bytes(self):
        """Test byte-sized values."""
        assert human_readable_size(1) == "1 B"
        assert human_readable_size(512) == "512 B"
        assert human_readable_size(999) == "999 B"

    def test_kilobytes(self):
        """Test kilobyte-sized values."""
        assert human_readable_size(1024) == "1.0 KB"
        assert human_readable_size(1536) == "1.5 KB"
        assert human_readable_size(10240) == "10.0 KB"

    def test_megabytes(self):
        """Test megabyte-sized values."""
        assert human_readable_size(1024 * 1024) == "1.0 MB"
        assert human_readable_size(1.5 * 1024 * 1024) == "1.5 MB"
        assert human_readable_size(10 * 1024 * 1024) == "10.0 MB"

    def test_gigabytes(self):
        """Test gigabyte-sized values."""
        assert human_readable_size(1024 * 1024 * 1024) == "1.0 GB"
        assert human_readable_size(1.5 * 1024 * 1024 * 1024) == "1.5 GB"
        assert human_readable_size(10 * 1024 * 1024 * 1024) == "10.0 GB"

    def test_terabytes(self):
        """Test terabyte-sized values."""
        assert human_readable_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        assert human_readable_size(1.5 * 1024 * 1024 * 1024 * 1024) == "1.5 TB"
        assert human_readable_size(10 * 1024 * 1024 * 1024 * 1024) == "10.0 TB"

    def test_preferred_unit(self):
        """Test that preferred_unit option works correctly."""
        # Test that KB is used when preferred
        assert human_readable_size(1024 * 1024, preferred_unit='KB') == "1024.0 KB"
        
        # Test that MB is used when preferred
        assert human_readable_size(1024 * 1024, preferred_unit='MB') == "1.0 MB"
        assert human_readable_size(1024, preferred_unit='MB') == "0.0 MB"
        
        # Test that GB is used when preferred
        assert human_readable_size(1024 * 1024 * 1024, preferred_unit='GB') == "1.0 GB"
        assert human_readable_size(1024 * 1024, preferred_unit='GB') == "0.0 GB"
        assert human_readable_size(500 * 1024 * 1024, preferred_unit='GB') == "0.5 GB"

    def test_decimal_places(self):
        """Test that decimal_places option works correctly."""
        assert human_readable_size(1536, decimal_places=1) == "1.5 KB"
        assert human_readable_size(1536, decimal_places=2) == "1.50 KB"
        assert human_readable_size(1536, decimal_places=3) == "1.500 KB"
        assert human_readable_size(1536, decimal_places=0) == "2 KB"

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Negative sizes should return appropriate string
        assert human_readable_size(-1) == "Invalid size"
        
        # Invalid preferred_unit should fall back to automatic selection
        assert human_readable_size(1024, preferred_unit='XB') == "1.0 KB"


@pytest.mark.unit
class TestFormatTimestamp:
    """Tests for the format_timestamp function."""

    def test_valid_timestamp(self):
        """Test that valid timestamps are formatted correctly."""
        # Test with a specific timestamp (January 1, 2023 00:00:00 UTC)
        assert format_timestamp(1672531200) == "2023-01-01 00:00:00"
        
    def test_none_timestamp(self):
        """Test that None is handled correctly."""
        assert format_timestamp(None) == "N/A"
        
    def test_invalid_timestamp(self):
        """Test handling of invalid timestamps."""
        assert format_timestamp("not a timestamp") == "N/A"


@pytest.mark.unit
class TestCategorizeFileByType:
    """Tests for the categorize_file_by_type function."""

    def test_document_types(self):
        """Test categorization of document file types."""
        assert categorize_file_by_type("file.pdf") == "Documents"
        assert categorize_file_by_type("file.docx") == "Documents"
        assert categorize_file_by_type("file.xlsx") == "Documents"
        assert categorize_file_by_type("file.txt") == "Documents"
    
    def test_image_types(self):
        """Test categorization of image file types."""
        assert categorize_file_by_type("image.jpg") == "Images"
        assert categorize_file_by_type("image.jpeg") == "Images"
        assert categorize_file_by_type("image.png") == "Images"
        assert categorize_file_by_type("image.gif") == "Images"
    
    def test_video_types(self):
        """Test categorization of video file types."""
        assert categorize_file_by_type("video.mp4") == "Videos"
        assert categorize_file_by_type("video.mov") == "Videos"
        assert categorize_file_by_type("video.avi") == "Videos"
    
    def test_audio_types(self):
        """Test categorization of audio file types."""
        assert categorize_file_by_type("audio.mp3") == "Audio"
        assert categorize_file_by_type("audio.wav") == "Audio"
        assert categorize_file_by_type("audio.flac") == "Audio"
    
    def test_archive_types(self):
        """Test categorization of archive file types."""
        assert categorize_file_by_type("archive.zip") == "Archives"
        assert categorize_file_by_type("archive.tar.gz") == "Archives"
        assert categorize_file_by_type("archive.rar") == "Archives"
    
    def test_code_types(self):
        """Test categorization of code file types."""
        assert categorize_file_by_type("code.py") == "Code"
        assert categorize_file_by_type("code.js") == "Code"
        assert categorize_file_by_type("code.java") == "Code"
    
    def test_unknown_types(self):
        """Test categorization of unknown file types."""
        assert categorize_file_by_type("file.xyz") == "Other"
        assert categorize_file_by_type("file") == "Other"
        assert categorize_file_by_type("") == "Other" 