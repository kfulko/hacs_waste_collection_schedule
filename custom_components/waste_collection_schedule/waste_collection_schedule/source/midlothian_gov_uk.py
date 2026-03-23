import datetime
import requests
from waste_collection_schedule import Collection

TITLE = "Midlothian Council"
DESCRIPTION = "Source script for my.midlothian.gov.uk bin collections"
URL = "https://my.midlothian.gov.uk/"
LOOKUP_ID_BIN_COLLECTION_SERVICE = "69a19ba76d3a2"
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
        session.get(SESSION_URL)
        today = datetime.date.today().strftime("%Y-%m-%d")
        payload = {
            "formValues": {
                "Section 1": {
                    "uprn": {"value": self._uprn},
                    "postcode": {"value": self._postcode},
                    "fromDate": {"value": today},
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        resp = session.post(API_URL, json=payload, headers=headers)
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
        for row in rows.values():
            date_str = row.get("Date")
            try:
                date = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S").date()
            except Exception:
                continue
            waste_type = row.get("Service")
            entries.append(
                Collection(
                    date=date,
                    t=waste_type,
                    icon=ICON_MAP.get(waste_type),
                )
            )
        return entries
