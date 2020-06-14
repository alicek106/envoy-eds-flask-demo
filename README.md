# EDS Demo for Envoy Proxy (using Flask)

This repository contains only minimum source code to use EDS. Just run `python3 main.py!`. Of course, don't forget to execute `pip3 install flask`

1. Run `pip3 install flask`
2. Run `python3 main.py`
3. Run Nginx Container
```bash
$ docker network create envoy_test
$ docker run -d --name nginx1 --network envoy_test -h nginx1 nginx
```

4. Register Endpoint resource to the EDS server
```bash
$ docker inspect nginx1 | grep IPAddress
            "SecondaryIPAddresses": null,
            "IPAddress": "",
                    "IPAddress": "172.18.0.2",

$ curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
  "hosts": [
    {
      "ip_address": "172.18.0.2",
      "port": 80,
      "tags": {
        "az": "ap-northeast-2a",
        "canary": false,
        "load_balancing_weight": 50
      }
    }
  ]
}' http://localhost:8080/eds/myservice

```

5. Confirm that endpoint has been registered.
```
curl -X POST \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    -d '{"resource_names":["myservice"]}' \
    localhost:8080/v2/discovery:endpoints | jq -r

{
  "version_info": "v1",
  "resources": [
    {
      "@type": "type.googleapis.com/envoy.api.v2.ClusterLoadAssignment",
      "cluster_name": "myservice",
      "endpoints": [
        {
          "lb_endpoints": [
            {
              "endpoint": {
                "address": {
                  "socket_address": {
                    "address": "172.18.0.2",
                    "port_value": 80
                  }
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

6. Change EDS Server IP to your Flask server accessible IP (usually host IP)
```bash
$ cat envoy.yaml
...
    connect_timeout: 0.25s
    hosts: [{ socket_address: { address: 172.20.10.2, port_value: 8080 }}]
```

7. RUN Envoy Proxy and Nginx Container
```bash
$ docker run -it --network envoy_test --rm -p 80:80 \
  -v $(pwd)/envoy.yaml:/tmp/envoy.yaml envoyproxy/envoy:v1.14.1 envoy -c /tmp/envoy.yaml
```

8. Send request to Envoy Proxy
```bash
$ curl localhost:80
```
