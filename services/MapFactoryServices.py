import os
from googleapiclient.errors import HttpError

from models.schemas import MapFactory

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def get_map_factories(service) -> list[list]:
    sheet_name = "MapFactories"
    read_range = f"{sheet_name}!A2:E"

    try:
        result = (
            service.spreadsheets()
                   .values()
                   .get(spreadsheetId=SPREADSHEET_ID, range=read_range)
                   .execute()
        )
        rows = result.get("values", [])
        return rows
    except HttpError as err:
        raise RuntimeError(f"Cannot read sheet: {err}")
def add_map_factories(service, new_factories:list[MapFactory]):
    sheet_name = "MapFactories"
    read_range = f"{sheet_name}!A:E"

    values_to_append = [
        [
            f.name,
            f.address,
            f.location.lat,
            f.location.lng,
            f.with_solar_panel,
        ]
        for f in new_factories
    ]
    body = {"values": values_to_append}
    try:
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=read_range,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
    except HttpError as err:
        raise RuntimeError(f"Cannot write on sheet: {err}")