import os
import re
from typing import Iterator

from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def limit_list(it: Iterator, value: int) -> Iterator:
    i = 0
    for item in it:
        if i < value:
            yield item
        else:
            break
        i += 1


def file_proces(f: Iterator, cmd: str, value: str) -> Iterator:
    result = map(lambda v: v.strip(), f)
    if cmd == 'filter':
        return filter(lambda v: value in v, result)
    if cmd == 'sort':
        return iter(sorted(result, reverse=bool(value)))
    if cmd == 'unique':
        return iter(set(result))
    if cmd == 'limit':
        return limit_list(result, int(value))
    if cmd == 'map':
        return map(lambda v: v.split(' ')[int(value)], result)
    if cmd == 'regex':
        reg = re.compile(value)
        return filter(lambda v: reg.search(v), result)
    return result


@app.route("/perform_query")
def perform_query() -> Response:
    try:
        cmd1 = request.args['cmd1']
        cmd2 = request.args['cmd2']
        value1 = request.args['value1']
        value2 = request.args['value2']
        file_name = request.args['file_name']
    except:
        raise BadRequest

    file = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file):
        raise BadRequest
    with open(file) as f:
        result = file_proces(f, cmd1, value1)
        result = file_proces(result, cmd2, value2)
        resultat = "\n".join(result)
    return app.response_class(resultat, content_type="text/plain")


app.run()
