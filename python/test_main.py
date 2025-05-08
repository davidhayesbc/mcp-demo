import pytest
import json
from main import whistler_weather

@pytest.mark.asyncio
async def test_whistler_weather(monkeypatch):
    # Mock the fetch_weather_data function
    async def mock_fetch_weather_data(url):
        with open("..\\test-data\\weather.html", "r") as file:
            return file.read()

    monkeypatch.setattr("main.fetch_weather_data", mock_fetch_weather_data)

    # Call the whistler_weather function
    result_data = await whistler_weather()

    # Validate the structure and content of the result
    assert "alpineForecast" in result_data
    assert "villageForecast" in result_data

    alpine_forecast = result_data["alpineForecast"]
    village_forecast = result_data["villageForecast"]

    # Validate alpineForecast
    assert alpine_forecast["CurrentTempMetric"] is not None
    assert alpine_forecast["HighTempMetric"] is not None
    assert alpine_forecast["LowTempMetric"] is not None
    assert alpine_forecast["WindSpeed"] is not None
    assert alpine_forecast["FreezingLevelMetric"] is not None
    assert alpine_forecast["SnowFallDayMetric"] is not None
    assert alpine_forecast["SnowFallNightMetric"] is not None
    assert alpine_forecast["Date"] is not None
    assert alpine_forecast["WeatherShortDescription"] is not None

    # Validate villageForecast
    assert village_forecast["CurrentTempMetric"] is not None
    assert village_forecast["HighTempMetric"] is not None
    assert village_forecast["LowTempMetric"] is not None
    assert village_forecast["WindSpeed"] is not None
    assert village_forecast["FreezingLevelMetric"] is None
    assert village_forecast["SnowFallDayMetric"] is None
    assert village_forecast["SnowFallNightMetric"] is None
    assert village_forecast["Date"] is not None
    assert village_forecast["WeatherShortDescription"] is not None

@pytest.mark.asyncio
async def test_whistler_weather_integration():
    """Integration test for whistler_weather that connects to the actual API."""
        
    # Call the actual whistler_weather function without mocking
    result_data = await whistler_weather()
    
    # Check that we don't have an error response
    assert "error" not in result_data
    
    # Validate the structure of the result
    assert "alpineForecast" in result_data
    assert "villageForecast" in result_data
    
    # Log the result for debugging purposes
    print(f"Integration test result: {json.dumps(result_data, indent=2, default=str)}")
    
    # Basic validation of data types and structure
    alpine_forecast = result_data["alpineForecast"]
    village_forecast = result_data["villageForecast"]
    
    # Check that at least one forecast was returned
    assert alpine_forecast is not None or village_forecast is not None
