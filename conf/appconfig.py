import os
import yaml

DEFAULTS = {
    'mongo': {
        'username': os.getenv('MONGO_USERNAME', ''),
        'password': os.getenv('MONGO_PASSWORD', ''),
        'url': os.getenv('MONGO_URL', 'mongodb://localhost:27017'),
        'includes': os.getenv('MONGO_INCLUDES', '')
    },
    'es': {
        'url': os.getenv('ES_URL', 'http://localhost:9200'),
        'indexes': yaml.load(os.getenv('ES_INDEXES') or '{}')

    }
}

CONFIG_LOCATION = os.getenv('CONFIG_LOCATION')
