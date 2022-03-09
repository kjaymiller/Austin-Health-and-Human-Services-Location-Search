from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from city_maps import get_places_location
import queries
from es_connection import es_client
import itertools
from icons import type_icons
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def cleanup_results(result):
    """Prep Results"""
    entry, sort = result['_source'], result.get('sort', None)
    doc = {}
    doc['name'] = entry['facility_name']
    doc['address'] = ", ".join(entry['street_address'].values())

    if entry['hours']:
        doc['hours'] = entry['hours'].split(';')

    doc['website'] = entry.get('website', "#")
    doc['phone'] = entry['phone']
    doc['type'] = entry.get('type', [])
    
    if sort:
       doc['distance'] = round(sort[0], 2)
    
    return doc

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    results = queries.agg_types()
    return templates.TemplateResponse("index.html", {"request": request, "results": results, "icons": type_icons})


@app.post("/search")
def search_location(
    request: Request,
    q: str=Form(...),
    ):
    """Returns a list of locations based on the search"""
    location_match = get_places_location(q)
    
    sort = [{
        "_geo_distance": {
            "location":  {
                "lat": location_match['location']['lat'],
                "lon": location_match['location']['lng']
            },
            "order": "asc",
            "unit": "mi",
        }
    }]
    results = es_client.search(sort=sort)
    result_docs = map(cleanup_results, results['hits']['hits'])
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "results": result_docs,
            "results_meta": results['hits'],
            "search_request": location_match
        },
        )


@app.get("/type/{_type}")
def get_by_type(request: Request, _type: str):
    search_results = queries.filter_types(_type)
    result_docs = list(map(cleanup_results, search_results['hits']['hits']))
    return templates.TemplateResponse(
        "by_type.html",
        {
            "request": request,
            "results": result_docs,
            "_type": _type
        }
    )