from es_connection import es_client
import typing

def agg_types(query: typing.Optional[dict[str, str]]= None ) -> dict[str,str]:
    """return all the values of type and their doc_counts"""
    if query == None:
        query = {
            "match_all": {}
        }

    aggs = {
        "by_type": {
            "terms": {
                "field": "type.keyword"
            }
        }
    }

    return es_client.search(query=query, aggs=aggs)



def filter_types(_type:str):
    query = {
        "match": {"type.keyword": _type}
    }

    return es_client.search(query=query, size=100)