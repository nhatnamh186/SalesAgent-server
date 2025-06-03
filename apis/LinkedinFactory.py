import os
import uuid
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, HTTPException, Depends, Query

from core.auth import (
    get_google_sheets_service
)
from models.schemas import LinkedinFactory, MapFactory

from services.LinkedinFactoryServices import  (
    get_linkedin_factories,
    add_linkedin_factories,
    delete_linkedin_factory_by_id,
    update_linkedin_factory_by_id,
    get_linkedin_factory_by_id
)
from services.ExpandiServices import send_messages

from scrap.scrapping import crawl, generate
MAP_KEY = os.environ.get("MAP_KEY")
GEMINI_KEY = os.environ.get("GEMINI_KEY")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.get("/linkedin-factories/get", response_model=list[LinkedinFactory])
async def get_linkedin_factories_api(
    sheets_service: dict = Depends(get_google_sheets_service)
):
    try:
        print("✅ Sheets service initialized successfully.")
        existing_rows = get_linkedin_factories(sheets_service)
        results = [
            LinkedinFactory(
                id=row[0],
                query=row[1],
                companyName=row[2],
                companyID=row[3],
                companyUrl=row[4],
                description=row[5],
                fullName=row[6],
                jobTitle=row[7],
                profileUrl=row[8],
                role=row[9],
                outreachMessage=row[10],
                status=row[11]
            )
            for row in existing_rows
        ]

        return results[::-1]

    except Exception as e:
        print("❌ Error reading LinkedIn factories:", e)
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@router.post("/linkedin-factories/add-new", response_model=dict)
async def add_new_factories(factories: list[MapFactory], sheets_service: dict = Depends(get_google_sheets_service) ):
    print(f"Get sheets service successful")
    try:
        if not factories:
            raise HTTPException(status_code=400, detail="No factory data provided.")

        existing_rows = get_linkedin_factories(sheets_service)
        existing_names = [row[1] for row in existing_rows]
        new_factories: list[LinkedinFactory] = []
        skipped = []

        for factory in factories:
            if factory.name in existing_names:
                skipped.append(factory.name)
                continue

            new_factory = LinkedinFactory(
                id=str(uuid.uuid4()),
                query=factory.name,
                status=0
            )
            new_factories.append(new_factory)
        if new_factories:
            add_linkedin_factories(sheets_service, new_factories)

        return {
            "added": [f.query for f in new_factories],
            "skipped": skipped,
            "total_added": len(new_factories),
            "total_skipped": len(skipped)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ {str(e)}")
    
@router.post("/linkedin-factories/crawl")
async def crawl_data(roles:list[str], sheets_service: dict = Depends(get_google_sheets_service)):
    try:
        datas = get_linkedin_factories(sheets_service)
        datas = [row for row in datas if str(row[-1]) == "0"]
        if len(datas) == 0:
            return {"message": "No data to crawl"}
        datas = datas[:10]
        print("len of datas:", len(datas))
        if not datas:
            raise HTTPException(status_code=404, detail="No data found in the sheet.")
        for data in datas:
            query = data[1]
            id = data[0]
            responses = crawl(query, id, roles)
            print("response", responses)
            #Delete data by id
            delete_linkedin_factory_by_id(sheets_service, id)
            for idx, response in enumerate(responses):
                response.id = response.id + str(idx)
            add_linkedin_factories(sheets_service, responses)
        print("Sucesssful")
        return {"message": "Successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/linkedin-factories/generate")
async def generate_data(sheets_service: dict = Depends(get_google_sheets_service)):
    try:
        datas = get_linkedin_factories(sheets_service)
        datas = [row for row in datas if str(row[-1]) == "1"]
        if len(datas) == 0:
            return {"message": "No data to generate"}
        datas = datas[:10]
        print("len of datas:", len(datas))
        if not datas:
            raise HTTPException(status_code=404, detail="No data found in the sheet.")
        for data in datas:
            response = generate({
                "id":data[0],
                "query":data[1],
                "companyName":data[2],
                "companyID":data[3],
                "companyUrl":data[4],
                "description":data[5],
                "fullName":data[6],
                "jobTitle":data[7],
                "profileUrl":data[8],
                "role":data[9],
                "outreachMessage":data[10],
                "status":data[11],
            })
            update_linkedin_factory_by_id(sheets_service, target_id=response.id, json_data=response)
        return {"message": "Data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/linkedin-factories/send-message")
async def generate_data(id: str = Query(...), sheets_service: dict = Depends(get_google_sheets_service)):
    try:
        data_obj = get_linkedin_factory_by_id(sheets_service, id)
        if not data_obj:
            raise HTTPException(status_code=404, detail="Data not found.")
        data = data_obj.model_dump()
        print(data)
        respone = send_messages(
            profile_link=data.get("profileUrl"),
            custom_placeholder=data.get("outreachMessage"),
        )
        respone = LinkedinFactory(
            id=id,
            query=data["query"],
            companyName=data["companyName"],
            companyID=data["companyID"],
            companyUrl=data["companyUrl"],
            description=data["description"],
            fullName=data["fullName"],
            jobTitle=data["jobTitle"],
            role=data["role"],
            profileUrl=data["profileUrl"],
            outreachMessage=data["outreachMessage"],
            status=3,
        )
        update_linkedin_factory_by_id(sheets_id=os.getenv("SPREADSHEET_ID"), sheets_name=os.getenv("SHEET_NAME"), target_id=id, json_data=respone)
        return {"message": "Data updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ {str(e)}")