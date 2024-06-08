import os

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


def influxdb_logger(pipe):
    
    token = os.getenv("IDB_TOKEN")
    org = os.getenv("IDB_ORG")
    bucket = os.getenv("IDB_BUCKET")
    url = os.getenv("IDB_URL")

    client = influxdb_client.InfluxDBClient(
       url=url,
       token=token,
       org=org
    )
    writer = client.write_api(write_options=SYNCHRONOUS)


    def gen():
        for item in pipe:
            if light := item.get("light", None):
                if light['light_level_valid']:
                    record = influxdb_client.Point("light_level")    \
                                        .tag("device", item['id'])  \
                                        .tag("product", item['owner']['product']) \
                                        .tag("name", item['owner']['name'])       \
                                        .field("light_level", light['light_level'])
            
                    writer.write(bucket=bucket, org=org, record=record)

            elif motion := item.get("motion", None):
                if motion['motion_valid']:
                    value = 1 if motion['motion'] else 0
                    record = influxdb_client.Point("motion")          \
                                        .tag("device", item['id'])  \
                                        .tag("product", item['owner']['product']) \
                                        .tag("name", item['owner']['name'])       \
                                        .field("motion", value)
            
                    writer.write(bucket=bucket, org=org, record=record)

            elif temp := item.get("temperature", None):
                if temp['temperature_valid']:
                    record = influxdb_client.Point("temperature")        \
                                        .tag("device", item['id'])  \
                                        .tag("product", item['owner']['product']) \
                                        .tag("name", item['owner']['name'])       \
                                        .field("temperature", temp['temperature'])
                
                    writer.write(bucket=bucket, org=org, record=record)
        
            yield item

    return gen()


