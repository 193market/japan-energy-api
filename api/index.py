from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Japan Energy API",
    description="Japan energy data including energy consumption, renewable energy share, fossil fuel dependency, electricity access, and CO2 intensity. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE_URL = "https://api.worldbank.org/v2/country/JP/indicator"

INDICATORS = {
    "energy_use":        {"id": "EG.USE.PCAP.KG.OE",  "name": "Energy Use Per Capita",          "unit": "kg of oil equivalent"},
    "renewable_share":   {"id": "EG.FEC.RNEW.ZS",     "name": "Renewable Energy Share",         "unit": "% of Total"},
    "fossil_fuel":       {"id": "EG.USE.COMM.FO.ZS",  "name": "Fossil Fuel Consumption",        "unit": "% of Total"},
    "electric_power":    {"id": "EG.USE.ELEC.KH.PC",  "name": "Electric Power Consumption",     "unit": "kWh per Capita"},
    "electricity_access":{"id": "EG.ELC.ACCS.ZS",     "name": "Access to Electricity",          "unit": "% of Population"},
    "co2_per_capita":    {"id": "EN.ATM.CO2E.PC",     "name": "CO2 Emissions Per Capita",       "unit": "Metric Tons"},
    "co2_intensity":     {"id": "EN.ATM.CO2E.EG.ZS",  "name": "CO2 Intensity of Energy",        "unit": "kg per kg oil equiv"},
    "nuclear_share":     {"id": "EG.ELC.NUCL.ZS",     "name": "Nuclear Energy Share",           "unit": "% of Total Electricity"},
}


async def fetch_wb(indicator_id: str, limit: int = 10):
    url = f"{WB_BASE_URL}/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


@app.get("/")
def root():
    return {
        "api": "Japan Energy API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "country": "Japan (JP)",
        "endpoints": [
            "/summary", "/energy-use", "/renewable", "/fossil-fuel",
            "/electricity", "/co2", "/nuclear"
        ],
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(limit: int = Query(default=5, ge=1, le=30)):
    """All Japan energy indicators snapshot"""
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb(meta["id"], limit)
    formatted = {
        key: {"name": INDICATORS[key]["name"], "unit": INDICATORS[key]["unit"], "data": results[key]}
        for key in INDICATORS
    }
    return {"country": "Japan", "country_code": "JP", "source": "World Bank Open Data", "updated_at": datetime.utcnow().isoformat() + "Z", "indicators": formatted}


@app.get("/energy-use")
async def energy_use(limit: int = Query(default=10, ge=1, le=60)):
    """Japan energy use per capita (kg of oil equivalent)"""
    data = await fetch_wb("EG.USE.PCAP.KG.OE", limit)
    return {"indicator": "Energy Use Per Capita", "series_id": "EG.USE.PCAP.KG.OE", "unit": "kg of oil equivalent", "frequency": "Annual", "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/renewable")
async def renewable(limit: int = Query(default=10, ge=1, le=60)):
    """Japan renewable energy share (% of total final energy consumption)"""
    data = await fetch_wb("EG.FEC.RNEW.ZS", limit)
    return {"indicator": "Renewable Energy Share", "series_id": "EG.FEC.RNEW.ZS", "unit": "% of Total Energy", "frequency": "Annual", "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/fossil-fuel")
async def fossil_fuel(limit: int = Query(default=10, ge=1, le=60)):
    """Japan fossil fuel energy consumption (% of total)"""
    data = await fetch_wb("EG.USE.COMM.FO.ZS", limit)
    return {"indicator": "Fossil Fuel Consumption", "series_id": "EG.USE.COMM.FO.ZS", "unit": "% of Total", "frequency": "Annual", "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/electricity")
async def electricity(limit: int = Query(default=10, ge=1, le=60)):
    """Japan electric power consumption per capita (kWh)"""
    data = await fetch_wb("EG.USE.ELEC.KH.PC", limit)
    return {"indicator": "Electric Power Consumption", "series_id": "EG.USE.ELEC.KH.PC", "unit": "kWh per Capita", "frequency": "Annual", "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/co2")
async def co2(limit: int = Query(default=10, ge=1, le=60)):
    """Japan CO2 emissions per capita and energy intensity"""
    per_cap = await fetch_wb("EN.ATM.CO2E.PC", limit)
    intensity = await fetch_wb("EN.ATM.CO2E.EG.ZS", limit)
    return {
        "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z",
        "co2_per_capita": {"series_id": "EN.ATM.CO2E.PC", "unit": "Metric Tons per Capita", "data": per_cap},
        "co2_intensity": {"series_id": "EN.ATM.CO2E.EG.ZS", "unit": "kg per kg oil equiv", "data": intensity},
    }


@app.get("/nuclear")
async def nuclear(limit: int = Query(default=10, ge=1, le=60)):
    """Japan nuclear energy share of electricity production (%)"""
    data = await fetch_wb("EG.ELC.NUCL.ZS", limit)
    return {"indicator": "Nuclear Energy Share", "series_id": "EG.ELC.NUCL.ZS", "unit": "% of Total Electricity", "frequency": "Annual", "country": "Japan", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)
    key = request.headers.get("X-RapidAPI-Key", "")
    if not key:
        return JSONResponse(status_code=401, content={"detail": "Missing X-RapidAPI-Key header"})
    return await call_next(request)
