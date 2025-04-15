import logging
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import re
import json
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

mcp = FastMCP("Whistler Weather)")

WHISTLER_WEATHER_API_URL = "https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"

async def fetch_weather_data(url: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
    }
    try:
        logging.info(f"Fetching weather data from URL: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            logging.info(f"Successfully fetched weather data from URL: {url}")
            return response.text
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

@mcp.resource("data://weather")
async def whistler_weather() -> dict:
    """Returns weather data for Whistler Blackcomb."""
    try:
        logging.info("Starting to fetch and parse weather data for Whistler.")
        html_content = await fetch_weather_data(WHISTLER_WEATHER_API_URL)
        
        # Extract the current weather summary information
        soup = BeautifulSoup(html_content, 'html.parser')
        weather_data = {}

        # Extract FR.forecasts JSON data from script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'FR.forecasts' in script.string:
                forecasts_match = re.search(r'FR\.forecasts\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if forecasts_match:
                    try:
                        logging.info("Parsing forecast JSON data.")
                        # Parse the JSON blob directly
                        weather_json = forecasts_match.group(1)
                        forecasts_json = json.loads(weather_json)
                        # Extract metric data from the forecasts JSON
                        metric_forecasts = []
                        for forecast in forecasts_json:
                            metric_forecast = {
                                "CurrentTempMetric": forecast.get("CurrentTempMetric"),
                                "HighTempMetric": forecast.get("HighTempMetric"),
                                "LowTempMetric": forecast.get("LowTempMetric"),
                                "WindSpeed": forecast.get("WindSpeed"),
                                "FreezingLevelMetric": forecast.get("FreezingLevelMetric"),
                                "SnowFallDayMetric": forecast.get("SnowFallDayMetric"),
                                "SnowFallNightMetric": forecast.get("SnowFallNightMetric"),
                                "Date": forecast.get("Date"),
                                "WeatherShortDescription": forecast.get("WeatherShortDescription"),
                            }
                            if "ForecastData" in forecast:
                                metric_forecast["ForecastData"] = [
                                    {
                                        "HighTempMetric": day.get("HighTempMetric"),
                                        "LowTempMetric": day.get("LowTempMetric"),
                                        "WindSpeed": day.get("WindSpeed"),
                                        "FreezingLevelMetric": day.get("FreezingLevelMetric"),
                                        "SnowFallDayMetric": day.get("SnowFallDayMetric"),
                                        "SnowFallNightMetric": day.get("SnowFallNightMetric"),
                                        "Date": day.get("Date"),
                                        "WeatherShortDescription": day.get("WeatherShortDescription"),
                                    }
                                    for day in forecast["ForecastData"]
                                ]
                            metric_forecasts.append(metric_forecast)
                        
                        # Assign the first and second elements to alpineForecast and villageForecast
                        weather_data["alpineForecast"] = metric_forecasts[0] if len(metric_forecasts) > 0 else None
                        weather_data["villageForecast"] = metric_forecasts[1] if len(metric_forecasts) > 1 else None
                        logging.info("Successfully parsed weather data.")
                        
                    except json.JSONDecodeError:
                        logging.error("Could not parse forecast JSON data.")
                        weather_data["forecast_parse_error"] = "Could not parse forecast JSON data"
                        break  # Exit loop if parsing fails
        logging.info("Weather data fetched and parsed successfully.")
        # Log the contents of weather_data
        logging.info(f"Weather data contents: {json.dumps(weather_data, indent=2, default=str)}")
        return weather_data
    except Exception as e:
        logging.error(f"Failed to fetch weather data: {str(e)}")
        return {"error": f"Failed to fetch weather data: {str(e)}"}
    
@mcp.resource("config://app-version")
def get_app_version() -> str:
    """Returns the application version."""
    return "v0.0.1"

@mcp.resource("data://product-categories")
def get_categories() -> list[str]:
    """Returns a list of available product categories."""
    return ["Electronics", "Books", "Home Goods"]