import json


def printer(pipe):
    
    def gen():
        for item in pipe:
            jdata = json.dumps(item, indent=2)
            print(jdata, flush=True)
            yield item

    return gen()

