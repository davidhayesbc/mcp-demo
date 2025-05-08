using MCPDemo;

namespace mcp_demo.tests
{
    public class WhistlerWeatherToolTests
    {
        [Fact]
        public async Task Weather_ReturnsValidWeatherResult()
        {
            // Act
            var result = await WhistlerWeatherTool.Weather();

            // Assert
            Assert.NotNull(result);
            Assert.NotNull(result.AlpineForecast);
            Assert.NotNull(result.VillageForecast);

            // Validate Alpine Forecast
            Assert.NotNull(result.AlpineForecast.Date);
            Assert.NotNull(result.AlpineForecast.WeatherShortDescription);

            // Validate Village Forecast
            Assert.NotNull(result.VillageForecast.Date);
            Assert.NotNull(result.VillageForecast.WeatherShortDescription);
        }
     }
}
