import datetime

import requests
from waste_collection_schedule import Collection
from waste_collection_schedule.exceptions import (
    SourceArgumentNotFound,
    SourceArgumentNotFoundWithSuggestions,
)

TITLE = "Ashfield District Council"
DESCRIPTION = "Source for ashfield.gov.uk, Ashfield District Council, UK"
URL = "https://www.ashfield.gov.uk"
TEST_CASES = {
    "11 Maun View Gardens, Sutton-in-Ashfield": {"uprn": 10001336299},
    "101 Main Street, Huthwaite": {"post_code": "NG17 2LQ", "uprn": "100031253415"},
    "1 Acacia Avenue, Kirkby-in-Ashfield": {"post_code": "NG17 9BH", "number": "1"},
    "Council Offices, Kirkby-in-Ashfield": {"post_code": "NG178ZA", "name": "COUNCIL OFFICES"}
}

API_URLS = {
    "address_search": "https://www.ashfield.gov.uk/api/address/search/{postcode}",
    "collection": "https://www.ashfield.gov.uk/api/address/collections/{uprn}",
}

ICON_MAP = {
    "Residual Waste Collection Service": "mdi:trash-can",
    "Domestic Recycling Collection Service": "mdi:recycle",
    "Domestic Glass Collection Service": "mdi:glass-fragile",
    "Garden Waste Collection Service": "mdi:leaf",
}

NAMES = {
    "Residual Waste Collection Service": "Red (rubbish)",
    "Domestic Recycling Collection Service": "Green (recycling)",
    "Domestic Glass Collection Service": "Blue (glass)",
    "Garden Waste Collection Service": "Brown (garden)",
}


class Source:
    def __init__(self, post_code=None, number=None, name=None, uprn=None):
        self._post_code = post_code
        self._number = number
        self._name = name
        self._uprn = uprn

    def fetch(self):
        if not self._uprn:
            # look up the UPRN for the address
            q = str(API_URLS["address_search"]).format(
                postcode=self._post_code)
            r = requests.get(q)
            r.raise_for_status()
            addresses = r.json()["results"]

            if not addresses:
                raise SourceArgumentNotFound("post_code", self._post_code)

            if self._name:
                matching = [
                    x for x in addresses if x["DPA"].get("BUILDING_NAME") and x["DPA"].get("BUILDING_NAME").capitalize() == self._name.capitalize()
                ]
                if matching:
                    self._uprn = int(matching[0]["DPA"]["UPRN"])
            elif self._number:
                matching = [
                    x for x in addresses if x["DPA"].get("BUILDING_NUMBER") == self._number
                ]
                if matching:
                    self._uprn = int(matching[0]["DPA"]["UPRN"])

            if not self._uprn:
                raise SourceArgumentNotFoundWithSuggestions(
                    argument="address",
                    value=f"{self._post_code} {self._number or self._name}",
                    suggestions=[f"{x['DPA'].get('BUILDING_NUMBER', '')} {x['DPA'].get('BUILDING_NAME', '')}".strip(
                    ) for x in addresses]
                )
        else:
            # Ensure UPRN is an integer
            self._uprn = int(self._uprn)

        q = str(API_URLS["collection"]).format(
            uprn=self._uprn
        )

        r = requests.get(q)
        r.raise_for_status()

        collections = r.json()["collections"]
        entries = []

        if collections:
            for collection in collections:
                entries.append(
                    Collection(
                        date=datetime.datetime.strptime(
                            collection["date"], "%d/%m/%Y %H:%M:%S"
                        ).date(),
                        t=NAMES.get(collection["service"]),
                        icon=ICON_MAP.get(collection["service"])
                    )
                )

        return entries
