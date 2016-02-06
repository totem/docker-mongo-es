import os
import yaml

MONGO_USERNAME = os.getenv('MONGO_USERNAME', None)
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', None)
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_INCLUDES = os.getenv('MONGO_INCLUDES', '')

ES_URL = os.getenv('ES_URL', 'http://localhost:9200')
ES_INDEXES = yaml.load(os.getenv('ES_INDEXES') or '{}')
ES_TIMEOUT_SECONDS = int(os.getenv('ES_TIMEOUT_SECONDS', '100'))

MONGO_CONNECTOR_CONFIG = 'mongo-connector.json'

DEFAULTS = {
    'es': {
        'url': ES_URL,
        'indexes': ES_INDEXES

    },
    'mongo-connector': {
        'mainAddress': MONGO_URL,
        'authentication': {
            'adminUsername': MONGO_USERNAME,
            'password': MONGO_PASSWORD
        },
        'namespaces': {
            'include': MONGO_INCLUDES.split(','),
        },
        'timezoneAware': True,
        'docManagers': [
            {
                'docManager': 'elastic_doc_manager',
                'targetURL': ES_URL,
                "args": {
                    "clientOptions": {
                        "timeout": ES_TIMEOUT_SECONDS
                    }
                }
            }
        ]
    }
}

CONFIG_LOCATION = os.getenv('CONFIG_LOCATION')
