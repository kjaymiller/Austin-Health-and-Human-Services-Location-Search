from os import environ
from elasticsearch import Elasticsearch
import os

es_client = Elasticsearch(
    hosts = ['https://localhost:9200'],
    basic_auth=(
        os.environ.get('ELASTIC_USER', ""),
        os.environ.get('ELASTIC_PWD', "")
    ),
    verify_certs=False,
)

if __name__ == "__main__":
    print(es_client.info())