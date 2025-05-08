namespace MCPDemo
{
  public class Forecast
  {
    public double? CurrentTempMetric { get; set; }
    public double? HighTempMetric { get; set; }
    public double? LowTempMetric { get; set; }
    public double? WindSpeed { get; set; }
    public double? FreezingLevelMetric { get; set; }
    public double? SnowFallDayMetric { get; set; }
    public double? SnowFallNightMetric { get; set; }
    public string Date { get; set; }
    public string WeatherShortDescription { get; set; }
    public List<ForecastDay> ForecastData { get; set; }
  }
}
