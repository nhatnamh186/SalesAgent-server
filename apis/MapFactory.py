import os
import asyncio
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, HTTPException, Depends

from core.auth import (
    get_current_user,
    get_google_sheets_service
)
from models.schemas import MapFactory
from services.GGMapServices import (
    search_places_in_area,
    download_satellite_image
)
from services.MapFactoryServices import  (
    get_map_factories,
    add_map_factories
)
from services.AiServices import SolarPanelDetector

MAP_KEY = os.environ.get("MAP_KEY")
GEMINI_KEY = os.environ.get("GEMINI_KEY")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/map-factories/get-nearby", response_model=list[MapFactory])
async def get_nearby_factories(
    lat: float,
    lon: float,
    radius: int = 1000,
    user: dict = Depends(get_current_user) 
):
    try:
        print(f"User {user['email']} verify successful")
        if not MAP_KEY:
            raise HTTPException(status_code=500, detail="API key not found.")

        all_results = []
        queries = [
            "factory", "nhà máy", "manufacturing", "xưởng"
        ]

        for query in queries:
            results = search_places_in_area(query, f"{lat},{lon}", radius, MAP_KEY)
            all_results.extend(results)

        unique_locations = set()
        unique_factories = []

        for place in all_results:
            loc = place["location"]
            location_key = (round(loc["lat"], 6), round(loc["lng"], 6))

            if location_key not in unique_locations:
                unique_locations.add(location_key)
                unique_factories.append({
                    "name": place["name"],
                    "address": place["address"],
                    "location": loc
                })

        return unique_factories

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ {str(e)}")

@router.post("/map-factories/check-solar-panels", response_model=list[MapFactory])
async def check_solar_panels(factories: list[MapFactory], sheets_service: dict = Depends(get_google_sheets_service) ):
    """
    Check each factory for solar panels, skip those already in sheet, and append new results.
    """
    print(f"Get sheets service successful")
    detector = SolarPanelDetector(GEMINI_KEY)
    # 1. Load existing factories from Google Sheet
    rows = get_map_factories(sheets_service)  # returns list of [name, address, lat, lng, with_solar_panel]
    # Build a lookup map for fast O(1) access
    existing_map: dict[tuple[str, float, float], int] = {}
    for row in rows:
        try:
            name, _, _, _, with_solar_panel = row
            key = name
            existing_map[key] = int(with_solar_panel)
        except (ValueError, IndexError):
            continue

    results: list[MapFactory] = []
    new_factories: list[MapFactory] = []
    loop = asyncio.get_running_loop()

    # 2. Process each factory
    for factory in factories:
        key = factory.name
        # If already exists, reuse the sheet value
        if key in existing_map:
            factory_result = factory.copy()
            factory_result.with_solar_panel = existing_map[key]
            results.append(factory_result)
            print(f"Factory {factory.name} - {factory_result.with_solar_panel} already exists in the sheet.")
            continue

        # Rate limiting
        await asyncio.sleep(2)

        # 3. Download satellite image (blocking) in executor
        filename = f"image.png"
        await loop.run_in_executor(
            None,
            download_satellite_image,
            factory.location.lat,
            factory.location.lng,
            MAP_KEY,
            filename
        )

        # 4. AI detection (blocking) in executor
        has_panel = await loop.run_in_executor(
            None,
            detector.check_solar_panel,
            filename
        )
        # 5. Build result
        factory_result = factory.copy()
        factory_result.with_solar_panel = 1 if has_panel == "Yes" else 0
        print(f"Factory {factory_result.name} - {factory_result.with_solar_panel} - {has_panel}")
        results.append(factory_result)
        new_factories.append(factory_result)

    # 6. Append new factories to sheet (if any)
    if new_factories:
        await loop.run_in_executor(None, add_map_factories, sheets_service, new_factories)

    return results