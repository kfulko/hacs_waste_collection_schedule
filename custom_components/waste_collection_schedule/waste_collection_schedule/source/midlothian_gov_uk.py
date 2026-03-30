import datetime
import requests
from waste_collection_schedule import Collection

TITLE = "Midlothian Council"
DESCRIPTION = "Source script for my.midlothian.gov.uk bin collections"
URL = "https://my.midlothian.gov.uk/"
LOOKUP_ID_BIN_COLLECTION_SERVICE = "69948bdca6012"
NO_RETRY = "false"
TEST_CASES = {
    "Test1": {"uprn": "120001401", "postcode": "EH26 8AG"},
}

API_URL = f"https://my.midlothian.gov.uk/apibroker/runLookup?id={LOOKUP_ID_BIN_COLLECTION_SERVICE}&noRetry={NO_RETRY}"
SESSION_URL = "https://my.midlothian.gov.uk/service/Bin_Collection_Dates"

ICON_MAP = {
    "Food Collection Service": "mdi:food-apple",
    "Glass Collection Service": "mdi:glass-fragile",
    "Residual Collection Service": "mdi:trash-can",
    "Garden Collection Service": "mdi:leaf",
    "Recycling Collection Service": "mdi:recycle",
    "Card Collection Service": "mdi:archive",
}

HOW_TO_GET_ARGUMENTS_DESCRIPTION = {
    "en": "Find your UPRN and postcode from your council documents or invoices.",
}

PARAM_DESCRIPTIONS = {
    "en": {
        "uprn": "Unique Property Reference Number (required)",
        "postcode": "Postcode of the property (required)",
    },
}

PARAM_TRANSLATIONS = {
    "en": {
        "uprn": "UPRN",
        "postcode": "Postcode",
    },
}

class Source:
    def __init__(self, uprn: str, postcode: str):
        self._uprn = uprn
        self._postcode = postcode

    def fetch(self):
        session = requests.Session()
        # Step 1: Get session id (sid) via isauthenticated
        auth_url = "https://my.midlothian.gov.uk/authapi/isauthenticated"
        auth_resp = session.get(auth_url)
        auth_resp.raise_for_status()
        auth_data = auth_resp.json()
        sid = auth_data.get("auth-session")
        if not sid:
            raise Exception(f"Failed to obtain session id (sid). Response: {auth_resp.text}")

        # Step 2: Prepare runLookup request with required params
        today = datetime.date.today()
        from_date = today.strftime("%Y-%m-%d")
        # API requires toDate - set to 1 year from now to get full year of collections
        to_date = (today.replace(year=today.year + 1)).strftime("%Y-%m-%d")
        payload = {
            "stopOnFailure": True,
            "usePHPIntegrations": True,
            "stage_id": "AF-Stage-a0bdbc4e-b9fc-46f0-bb0c-14a12cd927ed",
            "stage_name": "Stage 1",
            "formId": "AF-Form-033371a6-b0e4-4e16-a3b5-f68f592d8bf1",
            "formValues": {
                "Section 1": {
                    "UPRN": {"value": self._uprn},
                    "fromDate": {"value": from_date},
                    "toDate": {"value": to_date},
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        # Add sid and standard params to the URL
        runlookup_url = (
            f"https://my.midlothian.gov.uk/apibroker/runLookup?id={LOOKUP_ID_BIN_COLLECTION_SERVICE}"
            f"&sid={sid}&repeat_against=&noRetry={NO_RETRY}&getOnlyTokens=undefined&app_name=AF-Renderer::Self"
        )
        resp = session.post(runlookup_url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") == "logout":
            raise Exception("Session expired or invalid. Try again.")
        rows = (
            data.get("integration", {})
            .get("transformed", {})
            .get("rows_data", {})
        )
        entries = []
        failed_rows = []
        for row in rows.values():
            date_str = row.get("Date")
            try:
                date = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S").date()
            except (ValueError, TypeError, AttributeError) as e:
                # Track parsing failures - expected exceptions for invalid/missing dates
                failed_rows.append(f"Date='{date_str}': {type(e).__name__}")
                continue
            waste_type = row.get("Service")
            entries.append(
                Collection(
                    date=date,
                    t=waste_type,
                    icon=ICON_MAP.get(waste_type),
                )
            )

        # If we got rows but couldn't parse any, the format likely changed
        if rows and not entries:
            raise Exception(
                f"Failed to parse any collection dates from {len(rows)} rows. "
                f"API format may have changed. Failures: {failed_rows[:3]}"
            )

        return entries
