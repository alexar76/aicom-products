import pytest
from unittest.mock import AsyncMock, patch
from app.services.atlas_client import AtlasClient

@patch('httpx.AsyncClient.post', new_callable=AsyncMock)
async def test_invoke_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"ok": True, "receipt_digest": "abc"}
    client = AtlasClient()
    result = await client.invoke_situation_brief(55.7, 37.6)
    assert result["ok"] is True
    assert result["receipt_digest"] == "abc"

@patch('httpx.AsyncClient.post', new_callable=AsyncMock)
async def test_invoke_error(mock_post):
    mock_post.return_value.status_code = 500
    client = AtlasClient()
    result = await client.invoke_situation_brief(55.7, 37.6)
    assert result["ok"] is False
    assert "error" in result
