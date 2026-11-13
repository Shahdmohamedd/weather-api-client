import unittest
from unittest.mock import patch, MagicMock

import requests

import main

SAMPLE = {
    "location": {"name": "Cairo", "country": "Egypt"},
    "current": {"temp_c": 28.4, "feelslike_c": 29.1, "humidity": 40,
                "wind_kph": 13.0, "condition": {"text": "Sunny"}},
}


def fake_response(status=200, json_data=None, json_error=False):
    r = MagicMock()
    r.status_code = status
    r.ok = status < 400
    if json_error:
        r.json.side_effect = ValueError("bad json")
    else:
        r.json.return_value = json_data
    return r


class Tests(unittest.TestCase):
    def test_parse_and_summary(self):
        rep = main.WeatherReport.from_json(SAMPLE)
        self.assertEqual(rep.city, "Cairo")
        s = rep.summary()
        self.assertIn("Sunny", s)
        self.assertIn("28.4 °C", s)

    def test_bad_format(self):
        with self.assertRaises(main.WeatherError):
            main.WeatherReport.from_json({"location": {"name": "X"}})

    @patch("main.requests.get")
    def test_fetch_ok(self, get):
        get.return_value = fake_response(200, SAMPLE)
        self.assertEqual(main.fetch_weather("Cairo", "k").humidity, 40)

    @patch("main.requests.get")
    def test_401_404_500(self, get):
        for code in (400, 401, 403, 500):
            get.return_value = fake_response(code)
            with self.assertRaises(main.WeatherError):
                main.fetch_weather("Cairo", "k")

    @patch("main.requests.get")
    def test_network_and_json_errors(self, get):
        get.side_effect = requests.exceptions.ConnectionError("down")
        with self.assertRaises(main.WeatherError):
            main.fetch_weather("Cairo", "k")
        get.side_effect = None
        get.return_value = fake_response(200, json_error=True)
        with self.assertRaises(main.WeatherError):
            main.fetch_weather("Cairo", "k")

    @patch("main.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key(self, _):
        self.assertEqual(main.main([]), 1)

    @patch("main.requests.get")
    @patch("main.load_dotenv")
    @patch.dict("os.environ", {"API_KEY": "abc"}, clear=True)
    def test_main_success(self, _, get):
        get.return_value = fake_response(200, SAMPLE)
        self.assertEqual(main.main(["Cairo"]), 0)


if __name__ == "__main__":
    unittest.main()
