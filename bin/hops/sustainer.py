"""Sustain the event flow.

InfluxDB can give some strange looking graphs if there is a long time between samples. This
resends the event if more than 2 minutes has elapsed.
"""
import time


def sustainer(pipe, *, types=[]):
    
    types = { t.lower() for t in types }
    
    def gen():
        cache = {}
    
        for item in pipe:
            now = time.time()

            # if it's a valid item, cache it and yield it
            if iid := item.get('id', None):
                yield item
                
                # if it's a type to sustain, enter it into the cache
                etype = item['type']
                if len(types) == 0 or etype in types:
                    cache[iid] = (now, item)

            # check the cache for older items
            for k, v in cache.items():
                stamp = v[0]   # timestamp with this item was added to the cache
                citem = v[1]   # the cached item
                if now - stamp > 120:  # if more than 2 minutes has elapsed, yield it again
                    cache[k] = (now, citem)
                    citem['source'] = "cache"
                    yield citem
    
    return gen()

