import json
from elasticsearch import Elasticsearch
import sys
import mongo_connector.connector
import yaml
from conf.appconfig import CONFIG_LOCATION, DEFAULTS, MONGO_CONNECTOR_CONFIG
from mongo_es.util import requests_with_fs, dict_merge


def load_config(config_location=CONFIG_LOCATION):
    """
    Loads config and merges it with default config
    :param config_location:
    :return:
    """
    config = DEFAULTS
    if config_location:
        resp = requests_with_fs().get(config_location)
        if resp.status_code != 200:
            raise FileNotFoundError('Config was not found at location:{}'
                                    .format(config_location))
        loaded_config = yaml.load(resp.text)
        config = dict_merge(loaded_config, config)
    return config


def get_search_client(config):
    """
    Creates the elasticsearch client instance using SEARCH_SETTINGS

    :return: Instance of Elasticsearch
    :rtype: elasticsearch.Elasticsearch
    """
    return Elasticsearch(config['es']['url'])


def update_indexes(config):
    """
    Creates index mappings
    :param config:
    :return:
    """
    cl = get_search_client(config)
    for index, index_config in config['es'].get('indexes', {}).items():
        if not cl.indices.exists(index):
            cl.indices.create(index, index_config)
        else:
            for mapping_name, mapping in \
                    index_config.get('mappings', {}).items():
                cl.indices.put_mapping(mapping_name, mapping, index=index)


def create_connector_config(config, file):
    with open(file, 'w') as fp:
        json.dump(config['mongo-connector'], fp)


def launch():
    config = load_config()
    update_indexes(config)
    create_connector_config(config, MONGO_CONNECTOR_CONFIG)
    existing_args = sys.argv[1:]
    sys.argv = ['mongo-connector', '-c', MONGO_CONNECTOR_CONFIG] + \
        existing_args
    mongo_connector.connector.main()
