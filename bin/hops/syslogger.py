import syslog
import json


def syslogger(pipe):
    syslog.openlog(ident="hue-events", facility=syslog.LOG_LOCAL0)
    def gen():
        for item in pipe:
            jdata = json.dumps(item)
            syslog.syslog(syslog.LOG_INFO, jdata)
            yield item

    return gen()

