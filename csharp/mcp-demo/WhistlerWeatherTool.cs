using System.ComponentModel;
using System.Text.RegularExpressions;
using AngleSharp.Text;
using BrowseSharp;
using HtmlAgilityPack;
using ModelContextProtocol.Server;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace MCPDemo;

[McpServerToolType]
public static class WhistlerWeatherTool
{
    private const string WeatherUrl =
        "https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx";

    private const string UserAgent =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0";

    [McpServerTool]
    [Description("Returns weather data for Whistler Blackcomb.")]
    public static async Task<WeatherResult> Weather()
    {
        try
        {
            // Initialize BrowseSharp client
            var client = new Browser
            {
                //UserAgent = UserAgent
            };

            // Fetch the page
            var response = await client.NavigateAsync(WeatherUrl);
            if (response == null || response.Response == null || response.Response.StatusCode != System.Net.HttpStatusCode.OK)
                throw new InvalidOperationException($"Failed to fetch weather data: {response?.Response?.StatusCode}");

            // Get the HTML content
            var htmlContent = response.Response.Content;
            if (string.IsNullOrEmpty(htmlContent))
                throw new InvalidOperationException("Failed to fetch weather data: Empty HTML content");

            // Extract forecasts data directly with regex
            var forecastMatch = Regex.Match(htmlContent, @"FR\.forecasts\s*=\s*(\[.*?\]);", RegexOptions.Singleline);
            if (!forecastMatch.Success)
                throw new InvalidOperationException("Could not find weather forecast data in page.");

            try
            {
                var forecastsJson = forecastMatch.Groups[1].Value.Replace("Nil","0").Replace("Nil","0");
                var forecasts = JArray.Parse(forecastsJson);
                var forecastList = new List<Forecast>();

                foreach (var forecastToken in forecasts)
                {
                    var forecast = new Forecast
                    {
                        CurrentTempMetric = forecastToken["CurrentTempMetric"]?.Value<double?>(),
                        HighTempMetric = forecastToken["HighTempMetric"]?.Value<double?>(),
                        LowTempMetric = forecastToken["LowTempMetric"]?.Value<double?>(),
                        WindSpeed = forecastToken["WindSpeed"]?.Value<double?>(),
                        FreezingLevelMetric = forecastToken["FreezingLevelMetric"]?.Value<double?>(),
                        SnowFallDayMetric = forecastToken["SnowFallDayMetric"]?.Value<double?>(),
                        SnowFallNightMetric = forecastToken["SnowFallNightMetric"]?.Value<double?>(),
                        Date = forecastToken["Date"]?.Value<string>() ?? string.Empty,
                        WeatherShortDescription = forecastToken["WeatherShortDescription"]?.Value<string>() ?? string.Empty,
                        ForecastData = new List<ForecastDay>()
                    };

                    if (forecastToken["ForecastData"] != null)
                        foreach (var day in forecastToken["ForecastData"]!)
                            forecast.ForecastData.Add(new ForecastDay
                            {
                                HighTempMetric = day["HighTempMetric"]?.Value<double?>(),
                                LowTempMetric = day["LowTempMetric"]?.Value<double?>(),
                                WindSpeed = day["WindSpeed"]?.Value<double?>(),
                                FreezingLevelMetric = day["FreezingLevelMetric"]?.Value<double?>(),
                                SnowFallDayMetric = day["SnowFallDayMetric"]?.Value<double?>() ?? null,
                                SnowFallNightMetric = day["SnowFallNightMetric"]?.Value<double?>() ?? null,
                                Date = day["Date"]?.Value<string>() ?? null,
                                WeatherShortDescription = day["WeatherShortDescription"]?.Value<string>() ?? string.Empty
                            });

                    forecastList.Add(forecast);
                }

                var result = new WeatherResult
                {
                    AlpineForecast = forecastList.Count > 0 ? forecastList[0] : new Forecast(),
                    VillageForecast = forecastList.Count > 1 ? forecastList[1] : new Forecast()
                };
                return result;
            }
            catch (JsonException)
            {
                throw new JsonException("Could not parse forecast JSON data");
            }
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException($"Failed to fetch weather data: {ex.Message}");
        }
    }
}
