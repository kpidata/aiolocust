# encoding: utf-8
import os
import csv
import json
import logging
from io import StringIO

from time import time
from itertools import chain
from collections import defaultdict
import jinja2

import aiohttp_jinja2
from aiohttp import web
from flask import make_response

from aiolocust import runners
from aiolocust.cache import memoize
from aiolocust.runners import MasterLocustRunner
from aiolocust.stats import median_from_dict
from aiolocust import __version__ as version

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIME = 2.0


root_path = os.path.dirname(os.path.abspath(__file__))
app = web.Application()


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/swarm', swarm)
    app.router.add_get('/stop', stop)
    app.router.add_get('/stats/reset', reset_stats)
    app.router.add_get('/stats/requests/csv', request_stats_csv)
    app.router.add_get('/stats/distribution/csv', distribution_stats_csv)
    app.router.add_get('/stats/requests', request_stats)
    app.router.add_get('/exceptions', exceptions)
    app.router.add_get('/exceptions/csv', exceptions_csv)

    # Static files
    app.router.add_static('/static/', os.path.join(root_path, 'static'))


@aiohttp_jinja2.template('index.html')
def index(request):
    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        slave_count = runners.locust_runner.slave_count
    else:
        slave_count = 0
    
    return dict(
        state=runners.locust_runner.state,
        is_distributed=is_distributed,
        slave_count=slave_count,
        user_count=runners.locust_runner.user_count,
        version=version
    )


def swarm(request):
    assert request.method == "POST"

    locust_count = int(request.form["locust_count"])
    hatch_rate = float(request.form["hatch_rate"])
    runners.locust_runner.start_hatching(locust_count, hatch_rate)
    response = make_response(json.dumps({'success':True, 'message': 'Swarming started'}))
    response.headers["Content-type"] = "application/json"
    return response


def stop(request):
    runners.locust_runner.stop()
    response = make_response(json.dumps({'success':True, 'message': 'Test stopped'}))
    response.headers["Content-type"] = "application/json"
    return response


def reset_stats(request):
    runners.locust_runner.stats.reset_all()
    return "ok"


def request_stats_csv(request):
    rows = [
        ",".join([
            '"Method"',
            '"Name"',
            '"# requests"',
            '"# failures"',
            '"Median response time"',
            '"Average response time"',
            '"Min response time"', 
            '"Max response time"',
            '"Average Content Size"',
            '"Requests/s"',
        ])
    ]
    
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        rows.append('"%s","%s",%i,%i,%i,%i,%i,%i,%i,%.2f' % (
            s.method,
            s.name,
            s.num_requests,
            s.num_failures,
            s.median_response_time,
            s.avg_response_time,
            s.min_response_time or 0,
            s.max_response_time,
            s.avg_content_length,
            s.total_rps,
        ))

    response = make_response("\n".join(rows))
    file_name = "requests_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


def distribution_stats_csv(request):
    rows = [",".join((
        '"Name"',
        '"# requests"',
        '"50%"',
        '"66%"',
        '"75%"',
        '"80%"',
        '"90%"',
        '"95%"',
        '"98%"',
        '"99%"',
        '"100%"',
    ))]
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        if s.num_requests:
            rows.append(s.percentile(tpl='"%s",%i,%i,%i,%i,%i,%i,%i,%i,%i,%i'))
        else:
            rows.append('"%s",0,"N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"' % s.name)

    response = make_response("\n".join(rows))
    file_name = "distribution_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


@memoize(timeout=DEFAULT_CACHE_TIME, dynamic_timeout=True)
def request_stats(request):
    stats = []
    for s in chain(_sort_stats(runners.locust_runner.request_stats), [runners.locust_runner.stats.aggregated_stats("Total")]):
        stats.append({
            "method": s.method,
            "name": s.name,
            "num_requests": s.num_requests,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": s.min_response_time or 0,
            "max_response_time": s.max_response_time,
            "current_rps": s.current_rps,
            "median_response_time": s.median_response_time,
            "avg_content_length": s.avg_content_length,
        })
    
    report = {"stats":stats, "errors":[e.to_dict() for e in runners.locust_runner.errors.values()]}
    if stats:
        report["total_rps"] = stats[len(stats)-1]["current_rps"]
        report["fail_ratio"] = runners.locust_runner.stats.aggregated_stats("Total").fail_ratio
        
        # since generating a total response times dict with all response times from all
        # urls is slow, we make a new total response time dict which will consist of one
        # entry per url with the median response time as key and the number of requests as
        # value
        response_times = defaultdict(int) # used for calculating total median
        for i in range(len(stats)-1):
            response_times[stats[i]["median_response_time"]] += stats[i]["num_requests"]
        
        # calculate total median
        stats[len(stats)-1]["median_response_time"] = median_from_dict(stats[len(stats)-1]["num_requests"], response_times)
    
    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    if is_distributed:
        report["slave_count"] = runners.locust_runner.slave_count
    
    report["state"] = runners.locust_runner.state
    report["user_count"] = runners.locust_runner.user_count
    return web.Response(body=json.dumps(report).encode(),
                        content_type='application/json')


def exceptions(request):
    response = json.dumps({
        'exceptions': [
            {
                "count": row["count"], 
                "msg": row["msg"], 
                "traceback": row["traceback"], 
                "nodes" : ", ".join(row["nodes"])
            } for row in runners.locust_runner.exceptions.values()
        ]
    })
    return web.Response(text=response, content_type='application/json')


def exceptions_csv(request):
    data = StringIO()
    writer = csv.writer(data)
    writer.writerow(["Count", "Message", "Traceback", "Nodes"])
    for exc in runners.locust_runner.exceptions.values():
        nodes = ", ".join(exc["nodes"])
        writer.writerow([exc["count"], exc["msg"], exc["traceback"], nodes])
    
    data.seek(0)
    response = make_response(data.read())
    file_name = "exceptions_{0}.csv".format(time())
    disposition = "attachment;filename={0}".format(file_name)
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-disposition"] = disposition
    return response


def setup_app(app):
    templates_dir = os.path.join(root_path, 'templates')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates_dir))

    setup_routes(app)


def start(locust, options):
    # wsgi.WSGIServer((options.web_host, options.port), app, log=None).serve_forever()
    setup_app(app)
    web.run_app(app)


def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.keys())]
