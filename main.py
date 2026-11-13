"""Weather summary: calls the WeatherAPI.com REST API, parses the JSON,
stores it in a small class and prints a formatted summary."""
import os
import sys
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

API_URL = "https://api.weatherapi.com/v1/current.json"
TIMEOUT = 10  # seconds


class WeatherError(Exception):
    """Raised for any expected failure (missing key, bad city, network...)."""


@dataclass
class WeatherReport:
    city: str
    country: str
    description: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float  # km/h

    @classmethod
    def from_json(cls, data: dict) -> "WeatherReport":
        try:
            loc, cur = data["location"], data["current"]
            return cls(
                city=loc["name"],
                country=loc["country"],
                description=cur["condition"]["text"],
                temperature=float(cur["temp_c"]),
                feels_like=float(cur["feelslike_c"]),
                humidity=int(cur["humidity"]),
                wind_speed=float(cur["wind_kph"]),
            )
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise WeatherError(f"Unexpected API response format: {exc!r}") from exc

    def summary(self) -> str:
        line = "=" * 36
        return "\n".join([
            line,
            f" Weather in {self.city}, {self.country}",
            line,
            f" Condition   : {self.description.title()}",
            f" Temperature : {self.temperature:.1f} °C",
            f" Feels like  : {self.feels_like:.1f} °C",
            f" Humidity    : {self.humidity} %",
            f" Wind speed  : {self.wind_speed:.1f} km/h",
            line,
        ])


def fetch_weather(city: str, api_key: str) -> WeatherReport:
    params = {"key": api_key, "q": city, "aqi": "no"}
    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise WeatherError(f"Network error: {exc}") from exc

    if not response.ok:
        # WeatherAPI returns {"error": {"code": ..., "message": ...}}
        code = None
        try:
            code = response.json().get("error", {}).get("code")
        except (ValueError, AttributeError):
            pass
        if code == 1006:
            raise WeatherError(f"City '{city}' not found.")
        if response.status_code in (401, 403) or code in (1002, 2006, 2007, 2008, 2009):
            raise WeatherError("Invalid or disabled API key. Check your .env file.")
        raise WeatherError(f"API error: HTTP {response.status_code} (code {code})")

    try:
        data = response.json()
    except ValueError as exc:
        raise WeatherError("API did not return valid JSON.") from exc
    return WeatherReport.from_json(data)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    load_dotenv()  # reads .env into environment variables
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: API_KEY is missing. Put it in the .env file.", file=sys.stderr)
        return 1

    city = " ".join(argv) if argv else "Cairo"
    try:
        report = fetch_weather(city, api_key)
    except WeatherError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(report.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
