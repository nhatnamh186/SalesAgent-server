import os
import time
import pandas as pd
from urllib.parse import quote
from scrap.searchExport import SearchExport
from scrap.companyScraper import CompanyScraper
from scrap.companyURLFind import CompanyURLFinder
from services.AiServices import OutreachMessageGenerator
from models.schemas import LinkedinFactory
from utils.common import (
    phantom_fetch_output,
    getCSV
)

GEMINI_KEY = os.environ.get("GEMINI_KEY")
PHANTOM_KEY = os.environ.get("PHANTOM_KEY")
SEARCH_EXPORT_ID = os.environ.get("SEARCH_EXPORT_ID")
COMPANY_SCRAPER_ID = os.environ.get("COMPANY_SCRAPER_ID")
COMPANY_URL_FINDER_ID = os.environ.get("COMPANY_URL_FINDER_ID")
SESSION_COOKIE = os.environ.get("SESSION_COOKIE")
IDENTITY_ID = os.environ.get("IDENTITY_ID")

def create_outreach_message(row):
    if row["fullName"] == "" or row["jobTitle"] == "" or row["companyName"] == "" or row["description"] == "":
        return None
    time.sleep(2)
    generator = OutreachMessageGenerator(api_key=GEMINI_KEY)
    message = generator.generate_message(
        fullName=row["fullName"],
        jobTitle=row["jobTitle"],
        companyName=row["companyName"],
        description=row["description"],
        additional_context='''We’ve recently launched a new line of solar battery products that leverages advanced technology to enhance energy conversion efficiency and extend battery lifespan. 
        The solution is designed for both businesses and households seeking a more sustainable and cost-effective approach to energy usage. 
        I'm looking to connect with professionals in the clean energy space to exchange insights, explore potential collaborations, and discuss market opportunities where this solution can make a real impact.   
        ''',
        writing_style="Casual yet professional. Friendly greeting, acknowledges expertise, and includes a polite call to action."
    )
    return message
# roles = [
#         "CEO",  "Board Member", "Owner", "Partner", "Proprietor",
#         "Director", "Head of", "Principal", "Lead", "Leader",
#         "Manager", "Controller", "Treasurer", "Supervisor",
#         "Coordinator", "Senior"
#     ]
def simplify_url(url):
    return url.lower().replace("www.", "").rstrip("/")
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val)
def find_company_urls(query: str) -> str | None:
    try:
        # Initialize scraper
        scrapper = CompanyURLFinder(
            api_key=PHANTOM_KEY,
            agent_id=COMPANY_URL_FINDER_ID,
            spreadsheet_url=query,
        )

        def get_company_url_from_query():
            csv_url = phantom_fetch_output(
                COMPANY_URL_FINDER_ID,
                PHANTOM_KEY
            )
            if not csv_url:
                return None
            df = getCSV(csv_url, columns=["query", "linkedinUrl"])
            if df is None:
                print("df is None")
                return None
            elif df.empty:
                print("❌ CSV is empty")
                return None
            else:
                print("✅ CSV fetched successfully")
                match = df[df["query"] == query]
                print(match)
                if not match.empty:
                    return match["linkedinUrl"].iloc[0]
                return None
        # Try fetching URL before launching agent
        company_url = get_company_url_from_query()
        company_url = str(company_url)
        print(company_url)
        if company_url != 'None':
            if company_url == 'nan':
                print(f"❌ Company URL not found for query: {query}")
                return None
            print("✅ Found without scraping")
            return company_url
        # Launch scraping agent
        scrapper.launch_agent()

        # Try fetching URL again after scraping
        company_url = get_company_url_from_query()
        company_url = str(company_url)
        print(company_url)
        if company_url != 'None':
            if company_url == 'nan':
                print(f"❌ Company URL not found for query: {query}")
                return None
            print("✅ Found without scraping")
            return company_url

        print(f"❌ Company URL not found for query: {query}")
        return None

    except Exception as e:
        raise Exception(f"find_company_urls failed: {str(e)}")
def scrpap_company(companyURL:str, roles:list) -> tuple[dict, list[str]]:
    try:    
        # Initialize scraper
        scrapper = CompanyScraper(
            api_key=PHANTOM_KEY,
            agent_id=COMPANY_SCRAPER_ID,
            spreadsheetUrl=companyURL,
            sessionCookie=SESSION_COOKIE
        )
        def get_company_data_from_query():
            csv_url = phantom_fetch_output(
                COMPANY_SCRAPER_ID,
                PHANTOM_KEY
            )
            if not csv_url:
                return None
            df = getCSV(csv_url, columns=["companyName", "companyUrl", "mainCompanyID", "description"])
            print(df)
            if df is None:
                return None
            elif df.empty:
                print("❌ CSV is empty")
                return None
            else:
                print("✅ CSV fetched successfully")
                df = df.rename(columns={'mainCompanyID': 'companyID'})
                companyURL_simplified = simplify_url(companyURL)
                df["companyUrl"] = df["companyUrl"].apply(simplify_url)
                match = df[df["companyUrl"] == companyURL_simplified]
                if not match.empty:
                    data = match.iloc[0].to_dict()
                    company_id = data['companyID']
                    company_name = quote(data['companyName'])
                    search_urls = [
                        f"https://www.linkedin.com/search/results/people/?currentCompany=%5B%22{company_id}%22%5D"
                        f"&keywords={company_name}&titleFreeText={quote(role)}"
                        for role in roles
                    ]
                    return data, search_urls
                return None
        result = get_company_data_from_query()
        if result:
            data, search_urls = result
            if data and search_urls:
                print("✅ Found without scraping")
                return data, search_urls
        # Launch scraping agent
        scrapper.launch_agent()
        result = get_company_data_from_query()
        if result:
            data, search_urls = result
            if data and search_urls:
                print("✅ Found after scraping")
                return data, search_urls
        print(f"❌ Company data not found for URL: {companyURL}")
        return None, []
    except Exception as e:
        raise Exception(f"scrpap_company failed: {str(e)}")

def ExportProfiles(search_url:str) -> tuple[bool, str]:
    try:
        # Step 1: Export profiles from search agent
        scrapper = SearchExport(
            api_key=PHANTOM_KEY,
            agent_id=SEARCH_EXPORT_ID,
            linkedInSearchUrl=search_url,
            identityId=IDENTITY_ID,
            sessionCookie=SESSION_COOKIE,
        )
        def get_profile_from_search():
            csv_url = phantom_fetch_output(
                SEARCH_EXPORT_ID,
                PHANTOM_KEY
            )
            if not csv_url:
                return None
            df = getCSV(csv_url,columns=["query","fullName", "jobTitle","profileUrl", "error"])
            if df is None:
                return None
            elif df.empty:
                print("❌ CSV is empty")
                return None
            else:
                print("✅ CSV fetched successfully")
                match = df[df["query"] == search_url]
                if not match.empty:
                    data = match.iloc[0].to_dict()
                    if not data.get("error"):
                        return None
                    data.pop("error", None)
                    data.pop("query", None)
                    return data
                return None
        data = get_profile_from_search()
        if data:
            print("✅ Found without scraping")
            return data
        scrapper.launch_agent()
        data = get_profile_from_search()
        if data:
            print("✅ Found after scraping")
            return data
        print(f"❌ Profile data not found for URL: {search_url}")
        return None
    except Exception as e:
        raise Exception(f"ExportProfiles: {str(e)}")
def crawl(query:str, id:int, roles:list[str]) -> list[LinkedinFactory]:
    """
    Function to crawl LinkedIn profiles based on a given query.
    
    Args:
        query (str): The search query to use for crawling LinkedIn profiles.
    
    Returns:
        JSONResponse: The response containing the crawled data.
    """
    print(query)
  
    try:
        companyURL = find_company_urls(query)
        if not companyURL:
            return [LinkedinFactory(
                id=id,
                query=query,
                description="Company not found",
                status=4,
            )]
        print("Done step 1")
        # Step 2: Scrape company details
        company, search_urls = scrpap_company(companyURL,roles)
        if not company or not search_urls:
            return [LinkedinFactory(
                id=id,
                query=query,
                status=4,
            )]
        results = []
        print("Done step 2")
        print(company, search_urls)
        # Step 3: Export profiles and generate messages
        for idx, search_url in enumerate(search_urls):
            print("search_url", search_url)
            user = ExportProfiles(search_url)
            if not user:
                continue
            print("user", user) 
            profile_url = user.get("profileUrl")
            if not profile_url or pd.isna(profile_url):
                continue  
            data = user.copy()
            data["companyName"] = company["companyName"]
            data["companyUrl"] = company["companyUrl"]
            data["companyID"] = company["companyID"]
            data["description"] = company["description"]    
            data["role"] = query
            # Step 4: Generate outreach message
            data["outreachMessage"] = ""
            print("data", data)
            results.append(LinkedinFactory(
                id=id,
                query=query,
                companyName=safe_str(data["companyName"]),
                companyID=safe_str(data["companyID"]),
                companyUrl=safe_str(data["companyUrl"]),
                description=safe_str(data["description"]),
                fullName=safe_str(data["fullName"]),
                jobTitle=safe_str(data["jobTitle"]),
                profileUrl=safe_str(data["profileUrl"]),
                outreachMessage=safe_str(data["outreachMessage"]),
                role=roles[idx],
                status=1,
            ))
        print("Done step 3")
        print(len(results))
        if len(results) > 0:
            return results   
        print("No valid profiles found")
        return [LinkedinFactory(
            id=id,
            query=query,
            description="No valid profiles found",
            status=4,
        )]
    except Exception as e:
        raise Exception(f"crawl failed: {str(e)}")
def generate(data: dict) -> LinkedinFactory:
    """
    Function to crawl and generate outreach messages based on a given query.
    
    Args:
        data (str): The data to use for generate outreach message.
    
    Returns:
        data: The data with generated outreach message.
    """
    try:
        outreach_message = create_outreach_message(data)
        if outreach_message is None:
            return data
        data["outreachMessage"] = outreach_message
        print("data", data)
        return LinkedinFactory(
            id=data["id"],
            query=data["query"],
            companyName=safe_str(data["companyName"]),
            companyID=safe_str(data["companyID"]),
            companyUrl=safe_str(data["companyUrl"]),
            description=safe_str(data["description"]),
            fullName=safe_str(data["fullName"]),
            jobTitle=safe_str(data["jobTitle"]),
            profileUrl=safe_str(data["profileUrl"]),
            role=data["role"],
            outreachMessage=safe_str(data["outreachMessage"]),
            status=2,
        )
    except Exception as e:
        raise Exception(f"crawl_generate failed: {str(e)}")

    


    
    