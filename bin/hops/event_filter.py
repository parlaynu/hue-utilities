


def event_filter(pipe, types):
    
    types = set(types)

    def gen():
        for item in pipe:
            dtype = item['type']
            if len(types) > 0 and dtype not in types:
                continue
            yield item

    return gen()
