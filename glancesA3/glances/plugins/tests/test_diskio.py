import pytest
from unittest.mock import patch, MagicMock
import psutil
from glances.plugins.diskio import PluginModel  # Correctly using PluginModel


@pytest.fixture
def mock_psutil_disk_io_counters():
    """Fixture to mock psutil.disk_io_counters."""
    with patch('psutil.disk_io_counters') as mock_disk_io_counters:
        # Define the mock return value
        mock_disk_io_counters.return_value = MagicMock(
            read_bytes=1000,  # Simulate 1000 bytes read
            write_bytes=500   # Simulate 500 bytes written
        )
        yield mock_disk_io_counters  # Provide the mock to the test


# Test case for CRITICAL (very high read/write rates)
def test_get_color_critical(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
            'write_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is in the output


# Test case for WARNING (moderate read/write rates)
def test_get_color_warning(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 20 * 1024 * 1024,  # 20 MB/s (between WARNING threshold)
            'write_bytes_rate_per_sec': 15 * 1024 * 1024,  # 15 MB/s (between WARNING threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'WARNING' is in the result
    assert 'WARNING' in result[0]  # Check if the decoration 'WARNING' is in the output


# Test case for CAREFUL (low read/write rates)
def test_get_color_careful(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 5 * 1024 * 1024,  # 5 MB/s (between CAREFUL threshold)
            'write_bytes_rate_per_sec': 500 * 1024,      # 500 KB/s (below all thresholds)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CAREFUL' is in the result
    assert 'CAREFUL' in result[0]  # Check if the decoration 'CAREFUL' is in the output

# Test edge case for CRITICAL (just above threshold)
def test_get_color_critical_edge_case(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 51 * 1024 * 1024,  # 51 MB/s (just above CRITICAL threshold)
            'write_bytes_rate_per_sec': 51 * 1024 * 1024,  # 51 MB/s (just above CRITICAL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is in the output


# Test edge case for WARNING (just below threshold)
def test_get_color_warning_edge_case(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 49 * 1024 * 1024,  # 49 MB/s (just below WARNING threshold)
            'write_bytes_rate_per_sec': 38 * 1024 * 1024,  # 38 MB/s (just below WARNING threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'WARNING' is in the result
    assert 'WARNING' in result[0]  # Check if the decoration 'WARNING' is in the output


# Test edge case for CAREFUL (just below threshold)
def test_get_color_careful_edge_case(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 9 * 1024 * 1024,  # 9 MB/s (just below CAREFUL threshold)
            'write_bytes_rate_per_sec': 8 * 1024 * 1024,  # 8 MB/s (just below CAREFUL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CAREFUL' is in the result
    assert 'CAREFUL' in result[0]  # Check if the decoration 'CAREFUL' is in the output

# Test case for high read rate and low write rate (Critical read, default write)
def test_get_color_critical_read(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
            'write_bytes_rate_per_sec': 5 * 1024 * 1024,   # 5 MB/s (below CAREFUL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result for read and 'DEFAULT' or 'CAREFUL' is for write
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is for read
    assert 'CAREFUL' in result[0] or 'DEFAULT' in result[0]  # Check that write is either CAREFUL or DEFAULT


# Test case for low read rate and high write rate (Critical write, default or careful read)
def test_get_color_critical_write(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 5 * 1024 * 1024,   # 5 MB/s (below CAREFUL threshold)
            'write_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result for write and 'DEFAULT' or 'CAREFUL' is for read
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is for write
    assert 'CAREFUL' in result[0] or 'DEFAULT' in result[0]  # Check that read is either CAREFUL or DEFAULT


# Test case for high read rate and low write rate (Critical read, Careful write)
def test_get_color_critical_read_careful_write(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
            'write_bytes_rate_per_sec': 1 * 1024 * 1024,   # 1 MB/s (below CAREFUL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result for read and 'CAREFUL' for write
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is for read
    assert 'CAREFUL' in result[0]  # Check that write is CAREFUL


# Test case for low read rate and high write rate (Critical write, Careful read)
def test_get_color_careful_read_critical_write(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 1 * 1024 * 1024,   # 1 MB/s (below CAREFUL threshold)
            'write_bytes_rate_per_sec': 60 * 1024 * 1024,  # 60 MB/s (above CRITICAL threshold)
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that 'CRITICAL' is in the result for write and 'CAREFUL' for read
    assert 'CRITICAL' in result[0]  # Check if the decoration 'CRITICAL' is for write
    assert 'CAREFUL' in result[0]  # Check that read is CAREFUL

# Test case for very low rates (should be below all thresholds)
def test_get_color_no_warning(mock_psutil_disk_io_counters):
    plugin = PluginModel()
    plugin.stats = [
        {
            'disk_name': 'sda',
            'read_bytes_rate_per_sec': 0, 
            'write_bytes_rate_per_sec': 0,      
        }
    ]
    
    result = plugin.msg_curse()
    
    # Assert that no warning, careful, or critical decoration appears
    assert 'CAREFUL' not in result[0]  # Check that 'CAREFUL' is not in the result
    assert 'WARNING' not in result[0]  # Check that 'WARNING' is not in the result
    assert 'CRITICAL' not in result[0]   # Check that 'CRITICAL' is not in the result
