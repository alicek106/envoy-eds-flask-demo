import logging

from flask import Flask, request, Response
import json


class ServicesDAO(object):
    def __init__(self):
        self.services = {}

    def get(self, service_name):
        if service_name in self.services:
            return Response(json.dumps(self.services[service_name]), status=200, mimetype='application/json')
        return Response("Services {} doesn't exist".format(service_name), status=404)

    def create(self, service_name, data):
        if service_name in self.services:
            return Response("Services {} already exist".format(service_name), status=409)
        self.services[service_name] = data
        return Response("success", status=200, mimetype="application/json")


DAO = ServicesDAO()
app = Flask(__name__)


@app.route('/v2/discovery:endpoints', methods=['POST'])
def envoy_eds():
    data = json.loads(request.data)
    resource_names = data["resource_names"]
    print("Inbound v2 request for discovery. POST payload: " + str(data))

    for r in resource_names:
        if r in DAO.services:
            svc = DAO.services[r]
            endpoints = []
            for host in svc.get("hosts"):
                endpoints.append(
                    {
                        "endpoint": {
                            "address": {
                                "socket_address": {
                                    "address": host.get("ip_address"),
                                    "port_value": host.get("port")
                                }
                            }
                        }
                    }
                )
            resp = {
                "version_info": "v1",
                "resources": [
                    {
                        "@type": "type.googleapis.com/envoy.api.v2.ClusterLoadAssignment",
                        "cluster_name": r,
                        "type": "STRICT_DNS",
                        "endpoints": [
                            {
                                "lb_endpoints": endpoints
                            }
                        ]
                    }
                ]
            }
            return  Response(json.dumps(resp), status=200, mimetype='application/json')


@app.route('/eds/<string:service_name>', methods=['GET'])
def get_service(service_name):
    return DAO.get(service_name)


@app.route('/eds/<string:service_name>', methods=['POST'])
def create_service(service_name):
    data = request.get_json()
    return DAO.create(service_name, data)


if __name__ == '__main__':
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
    app.run(debug=True, host='0.0.0.0', port=8080)
