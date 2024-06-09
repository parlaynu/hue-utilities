


def event_filter(pipe, *, types=[]):
    
    types = { t.lower() for t in types }

    def gen():
        for item in pipe:
            etype = item['type']
            if len(types) > 0 and etype not in types:
                continue
            yield item

    return gen()
