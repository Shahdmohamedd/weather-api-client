# Weather Summary (WeatherAPI.com + .env + venv)

## Setup
1. Get a free API key from https://www.weatherapi.com (key is available right after sign-up).
2. Create the virtual environment and install dependencies:

   Linux / macOS:
       python3 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt

   Windows (PowerShell):
       python -m venv venv
       venv\Scripts\Activate.ps1
       pip install -r requirements.txt

3. Create `.env` from the example and paste your key:
       cp .env.example .env        (Windows: copy .env.example .env)
   Then edit it:  API_KEY=your_real_key

## Run
    python main.py            # default city: Cairo
    python main.py Alexandria

## Test (no API key or internet needed)
    python -m unittest -v
