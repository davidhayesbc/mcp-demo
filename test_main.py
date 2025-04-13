import pytest
import asyncio
from unittest.mock import patch, Mock
import json
import os

from main import fetch_weather_data, whistler_weather

# Path to the HTML test file
WHISTLER_HTML_PATH = os.path.join(os.path.dirname(__file__), "whistler.html")


@pytest.fixture
def sample_html():
    """Load the sample HTML file for testing."""
    with open(WHISTLER_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.mark.asyncio
async def test_fetch_weather_data():
    """Test the fetch_weather_data function with a mock response."""
    # Load the HTML test file dynamically
    with open(WHISTLER_HTML_PATH, "r", encoding="utf-8") as f:
        mock_html = f.read()

    # Create a mock response
    mock_response = Mock()
    mock_response.text = mock_html
    mock_response.raise_for_status = Mock()

    # Create a mock client that returns our mock response
    mock_client = Mock()
    mock_client.__aenter__.return_value = Mock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    mock_client.__aexit__ = Mock()

    # Patch the httpx.AsyncClient to return our mock client
    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await fetch_weather_data("https://test-url.com")
    
    assert result == mock_html
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_weather_data_http_error():
    """Test error handling in fetch_weather_data when HTTP error occurs."""
    # Create a mock client that raises an HTTPStatusError
    mock_client = Mock()
    mock_client.__aenter__.return_value = Mock()
    mock_client.__aenter__.return_value.get.side_effect = Exception("HTTP Error")
    mock_client.__aexit__ = Mock()

    # Patch the httpx.AsyncClient to return our mock client
    with patch('httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(Exception, match="HTTP Error"):
            await fetch_weather_data("https://test-url.com")


@pytest.mark.asyncio
async def test_whistler_weather(sample_html):
    """Test the whistler_weather function with sample HTML."""
    # Mock the fetch_weather_data function to return the loaded HTML
    async def mock_fetch_weather_data(*args, **kwargs):
        return sample_html

    with patch('main.fetch_weather_data', side_effect=mock_fetch_weather_data):
        result = await whistler_weather()
    
    # Check that the function executed successfully
    assert "Weather data fetched successfully" in result
    
    # Parse the JSON from the returned string
    json_str = result.replace("Weather data fetched successfully: ", "")
    weather_data = json.loads(json_str)
    
    # Check that the expected keys exist in the response
    assert "current_conditions" in weather_data
    assert "summary" in weather_data["current_conditions"]
    
    # Verify some of the extracted data
    if "temperature_high" in weather_data["current_conditions"]:
        assert weather_data["current_conditions"]["temperature_high"] == "High -1 °C"
    
    if "freezing_level" in weather_data["current_conditions"]:
        assert weather_data["current_conditions"]["freezing_level"] == "1700 metres"


@pytest.mark.asyncio
async def test_whistler_weather_error_handling():
    """Test error handling in whistler_weather function."""
    # Mock fetch_weather_data to raise an exception
    with patch('main.fetch_weather_data', side_effect=Exception("Test error")):
        result = await whistler_weather()
    
    assert "Failed to fetch weather data" in result
    assert "Test error" in result


@pytest.mark.asyncio
async def test_extract_fr_forecasts(sample_html):
  """Test extraction of FR.forecasts JSON from script tags."""
  async def mock_fetch_weather_data(*args, **kwargs):
    return sample_html

  with patch('main.fetch_weather_data', side_effect=mock_fetch_weather_data):
    result = await whistler_weather()
  
  # Check that the forecasts were extracted
  assert "Weather data fetched successfully" in result
  
  # Parse the JSON from the returned string
  json_str = result.replace("Weather data fetched successfully: ", "")
  weather_data = json.loads(json_str)
  
  # Check that the detailed_forecasts were extracted
  assert "detailed_forecasts" in weather_data
  assert "day1" in weather_data["detailed_forecasts"]
  assert "day2" in weather_data["detailed_forecasts"]
  
  # Verify the extracted data matches the HTML content
  assert weather_data["detailed_forecasts"]["day1"]["high"] == "High -1 °C"
  assert weather_data["detailed_forecasts"]["day1"]["low"] == "Low -5 °C"
  assert weather_data["detailed_forecasts"]["day2"]["high"] == "High 0 °C"
  assert weather_data["detailed_forecasts"]["day2"]["low"] == "Low -3 °C"
