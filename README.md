# Japan Energy API

Japan energy data including total energy use, renewable energy share, fossil fuel dependency, electricity consumption, nuclear energy share, and CO2 intensity. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All energy indicators snapshot |
| `GET /energy-use` | Energy use per capita |
| `GET /renewable` | Renewable energy share |
| `GET /fossil-fuel` | Fossil fuel consumption |
| `GET /electricity` | Electric power consumption per capita |
| `GET /co2` | CO2 emissions and energy intensity |
| `GET /nuclear` | Nuclear energy share |

## Data Source

World Bank Open Data
https://data.worldbank.org/country/JP

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
