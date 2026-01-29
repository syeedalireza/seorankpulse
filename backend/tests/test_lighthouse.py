"""
Tests for Lighthouse integration.
"""

import pytest
from app.services.lighthouse.lighthouse_client import LighthouseClient, interpret_core_web_vitals


@pytest.mark.asyncio
async def test_lighthouse_client_initialization():
    """Test Lighthouse client can be initialized."""
    client = LighthouseClient()
    assert client is not None
    assert client.chrome_flags is not None


def test_interpret_core_web_vitals():
    """Test Core Web Vitals interpretation."""
    cwv = {
        'lcp': 2.0,  # Good
        'cls': 0.05,  # Good
        'fid_estimate': 80,  # Good
    }
    
    interpretation = interpret_core_web_vitals(cwv)
    
    assert interpretation['lcp_status'] == 'good'
    assert interpretation['cls_status'] == 'good'
    assert interpretation['fid_status'] == 'good'
    assert interpretation['overall'] == 'good'


def test_interpret_core_web_vitals_poor():
    """Test Core Web Vitals interpretation for poor scores."""
    cwv = {
        'lcp': 5.0,  # Poor
        'cls': 0.3,  # Poor
        'fid_estimate': 400,  # Poor
    }
    
    interpretation = interpret_core_web_vitals(cwv)
    
    assert interpretation['lcp_status'] == 'poor'
    assert interpretation['cls_status'] == 'poor'
    assert interpretation['fid_status'] == 'poor'
    assert interpretation['overall'] == 'poor'
