import copy
import requests
import os


def dict_merge(*dictionaries):
    """
    Performs nested merge of multiple dictionaries. The values from
    dictionaries appearing first takes precendence

    :param dictionaries: List of dictionaries that needs to be merged.
    :return: merged dictionary
    :rtype
    """

    merged_dict = {}

    def merge(source, defaults):
        source = copy.deepcopy(source)
        # Nested merge requires both source and defaults to be dictionary
        if isinstance(source, dict) and isinstance(defaults, dict):
            for key, value in defaults.items():
                if key not in source:
                    # Key not found in source : Use the defaults
                    source[key] = value
                else:
                    # Key found in source : Recursive merge
                    source[key] = merge(source[key], value)
        return source

    for merge_with in dictionaries:
        merged_dict = merge(merged_dict, copy.deepcopy(merge_with or {}))

    return merged_dict


class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):
        """Return the file specified by the given request

        @type req: C{PreparedRequest}
        @todo: Should I bother filling `response.headers` and processing
               If-Modified-Since and friends using `os.stat`?
        """
        path = os.path.normcase(os.path.normpath(req.path_url))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass


def requests_with_fs():
    """
    Creates a request session with local file system support
    :return: Requests Session
    :rtype: requests.sessions.Session
    """
    requests_session = requests.session()
    requests_session.mount('file://', LocalFileAdapter())
    return requests_session
