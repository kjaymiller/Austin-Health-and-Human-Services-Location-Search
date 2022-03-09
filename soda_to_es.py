from sodapy import Socrata
from es_connection import es_client
from elasticsearch.helpers import bulk
import typing
import os
import json

dataset_id = "6v78-dj3u"
domain = "data.austintexas.gov"

socrata_client = Socrata(domain, os.environ.get("SOCRATA_API_KEY"))


def bulk_upload():
    soda_data = socrata_client.get_all(dataset_id)

    for entry in soda_data:
        doc = {
            "facility_name": entry.get("facility_name", None),
            "phone": entry.get("phone_number", None),
            "hours": entry.get("hours", None),
        }

        if website := entry.get("website", None):
            doc["website"] = website["url"]

        if entry.get("occupancy_type", None):
            doc["type"] = [x.strip() for x in entry.get("occupancy_type").split(",")]

        if entry.get("street_address", None):
            doc["location"] = {
                "lon": entry["street_address"]["longitude"],
                "lat": entry["street_address"]["latitude"],
            }
            doc['street_address'] = json.loads(entry['street_address']['human_address'])
        yield doc


mappings = {
    "properties": {
        "location": {"type": "geo_point"},
    }
}

if __name__ == "__main__":
    es_client.options(ignore_status=[404]).indices.delete(
        index="austin-health-human-svc-apr-2021"
    )
    es_client.indices.create(
        index="austin-health-human-svc-apr-2021", mappings=mappings
    )
    bulk(
        client=es_client,
        index="austin-health-human-svc-apr-2021",
        actions=bulk_upload(),
    )
