from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import re
import json
from bs4 import BeautifulSoup

mcp = FastMCP("Whistler Weather)")

WHISTLER_WEATHER_API_URL = "https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

async def fetch_weather_data(url: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        raise
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

@mcp.tool("whistler_weather", "Fetches the latest weather data from Whistler Blackcomb")
async def whistler_weather() -> str:
    """Fetches the latest weather data from Whistler Blackcomb"""
    try:
        html_content = await fetch_weather_data(WHISTLER_WEATHER_API_URL)
        
        # Extract the current weather summary information
        soup = BeautifulSoup(html_content, 'html.parser')
        weather_summary = soup.select_one(".container.component_container p")
        
        weather_data = {
            "current_conditions": {}
        }
        
        if weather_summary:
            weather_text = weather_summary.get_text(strip=True)
            weather_data["current_conditions"]["summary"] = weather_text
            
            # Extract temperature, wind and freezing level
            temp_match = re.search(r'Alpine Temperature: High (-?\d+) °C', weather_text)
            if temp_match:
                weather_data["current_conditions"]["temperature_high"] = f"{temp_match.group(1)}°C"
                
            wind_match = re.search(r'Wind (.*?)\.', weather_text)
            if wind_match:
                weather_data["current_conditions"]["wind"] = wind_match.group(1)
                
            freezing_match = re.search(r'Freezing Level: (\d+) metres', weather_text)
            if freezing_match:
                weather_data["current_conditions"]["freezing_level"] = f"{freezing_match.group(1)} metres"
        
        # Look for forecast data in the next paragraph
        forecast_element = soup.select_one(".container.component_container p span[data-teams='true']")
        if forecast_element:
            weather_data["forecast"] = forecast_element.get_text(strip=True)
            
        # Extract FR.forecasts JSON data from script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'FR.forecasts' in script.string:
                forecasts_match = re.search(r'FR\.forecasts\s*=\s*(\{.+?\});', script.string, re.DOTALL)
                if forecasts_match:
                    try:
                        # Parse the JSON blob directly
                        forecasts_json = json.loads(forecasts_match.group(1))
                        weather_data["detailed_forecasts"] = forecasts_json
                    except json.JSONDecodeError:
                        weather_data["forecast_parse_error"] = "Could not parse forecast JSON data"
                        break  # Exit loop if parsing fails
        
        return f"Weather data fetched successfully: {json.dumps(weather_data, indent=2)}"
    except Exception as e:
        return f"Failed to fetch weather data: {str(e)}"