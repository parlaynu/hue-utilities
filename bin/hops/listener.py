import json


def listener(client):
    
    # get the devices
    devices = client.get_devices()
    
    # start listening for events
    headers = {
        "Accept": "text/event-stream"
    }
    prefix = "data: "
    
    resp = client.get("/eventstream/clip/v2", extra_headers=headers, stream=True, timeout=300)
    
    def gen():
        for line in resp.iter_lines():
            line = line.decode('utf-8')
            if len(line) == 0:
                continue
            
            if not line.startswith(prefix):
                continue
            
            line = line[len(prefix):]
            events = json.loads(line)
        
            for event in events:
                datas = event['data']
                for data in datas:
                    # drop events with no owner
                    owner = data.get("owner", None)
                    if owner is None:
                        continue
                
                    # drop events of the owner isn't a device
                    if owner['rtype'] != 'device':
                        continue
                
                    # add some extra data from the top level event
                    data['event_stamp'] = event['creationtime']
                    data['event_id'] = event['id']
                    data['event_type'] = event['type']
                
                    owner_id = owner['rid']
                    if owner := devices.get(owner_id, None):
                        data['owner'] = owner
                
                    yield data
    
    return gen()

