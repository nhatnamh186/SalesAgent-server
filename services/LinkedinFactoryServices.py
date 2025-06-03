import os
from googleapiclient.errors import HttpError

from models.schemas import LinkedinFactory

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def get_linkedin_factories(service) -> list[list]:
    sheet_name = "LinkedinFactories"
    read_range = f"{sheet_name}!A2:L"

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

def add_linkedin_factories(service, new_factories:list[LinkedinFactory]):
    print(new_factories)
    sheet_name = "LinkedinFactories"
    read_range = f"{sheet_name}!A:L"

    values_to_append = [
        [
            f.id,
            f.query,
            f.companyName,
            f.companyID,
            f.companyUrl,
            f.description,
            f.fullName,
            f.jobTitle,
            f.profileUrl,
            f.role,
            f.outreachMessage,
            f.status
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
    
def delete_linkedin_factory_by_id(service, factory_id: str):
    print(factory_id)
    sheet_name = "LinkedinFactories"
    read_range = f"{sheet_name}!A2:A"

    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=read_range)
            .execute()
        )
        rows = result.get("values", [])

        row_index = None
        for i, row in enumerate(rows):
            if row and row[0] == factory_id:
                row_index = i + 1 + 1 
                break

        if row_index is None:
            raise ValueError(f"Factory with ID {factory_id} not found.")

        body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": 899135484,
                            "dimension": "ROWS",
                            "startIndex": row_index - 1,
                            "endIndex": row_index,
                        }
                    }
                }
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body
        ).execute()

    except HttpError as err:
        raise RuntimeError(f"Failed to delete row: {err}")
def update_linkedin_factory_by_id(sheets_service, target_id: str, json_data):
    sheet_name = "LinkedinFactories"
    read_range = f"{sheet_name}!A2:A"
    update_range_prefix = f"{sheet_name}!"
    
    try:
        # Lấy tất cả các ID trong cột A (bắt đầu từ hàng 2)
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=read_range
        ).execute()
        values = result.get("values", [])

        row_index = None
        for i, row in enumerate(values):
            if row and row[0] == target_id:
                row_index = i + 2  # +2 vì bắt đầu từ A2 nên index=0 => row 2
                break

        if row_index is None:
            raise ValueError(f"Factory with ID {target_id} not found.")

        # Dữ liệu cần cập nhật
        update_values = [[
            json_data.id,
            json_data.query,
            json_data.companyName,
            json_data.companyID,
            json_data.companyUrl,
            json_data.description,
            json_data.fullName,
            json_data.jobTitle,
            json_data.profileUrl,
            json_data.role,
            json_data.outreachMessage,
            json_data.status,
        ]]

        update_range = f"{update_range_prefix}A{row_index}:L{row_index}"

        sheets_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=update_range,
            valueInputOption="RAW",
            body={"values": update_values}
        ).execute()

    except HttpError as err:
        raise RuntimeError(f"Failed to update row: {err}")
def get_linkedin_factory_by_id(sheets_service, target_id: str) -> LinkedinFactory:
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    range_name = f"{sheet_name}!A2:L"  # Assuming headers are in row 1

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    rows = result.get("values", [])
    for row in rows:
        if len(row) > 0 and row[0] == target_id:
            return LinkedinFactory(
                id=row[0],
                query=row[1] if len(row) > 1 else "",
                companyName=row[2] if len(row) > 2 else "",
                companyID=row[3] if len(row) > 3 else "",
                companyUrl=row[4] if len(row) > 4 else "",
                description=row[5] if len(row) > 5 else "",
                fullName=row[6] if len(row) > 6 else "",
                jobTitle=row[7] if len(row) > 7 else "",
                profileUrl=row[8] if len(row) > 8 else "",
                role=row[9] if len(row) > 9 else "",
                outreachMessage=row[10] if len(row) > 10 else "",
                status=row[11] if len(row) > 11 else "",
            )

    return None

