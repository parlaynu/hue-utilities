import ipaddress
import threading

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf


class MyListener(ServiceListener):
    
    def __init__(self, sem):
        self._sem = sem
    
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        # print(f"updated {name}")
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        # print(f"removed {name}")
        pass

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        # print(f"added {name}")
        try:
            self.info = zc.get_service_info(type_, name)
        finally:
            self._sem.release()


class Bridge:
    def __init__(self, info):
        self.id = info.properties[b'bridgeid'].decode('utf-8')
        self.model_id = info.properties[b'modelid'].decode('utf-8')
        self.hostname = info.server
        self.port = info.port
        self.addresses = []
        for address in info.addresses:
            addr = ipaddress.ip_address(address)
            self.addresses.append(addr)
        self.address = self.addresses[0]


def find_bridge(ip_addr=None):
    unicast = False if ip_addr is None else True
    zeroconf = Zeroconf(unicast=unicast)

    # create a semaphore to signal from listener thread
    sem = threading.Semaphore(value=0)
    listener = MyListener(sem)
    browser = ServiceBrowser(zeroconf, "_hue._tcp.local.", listener, addr=ip_addr)

    # wait on the semaphore
    success = True
    if sem.acquire(timeout=10) == False:
        success = False
        browser.cancel()
    
    zeroconf.close()
    
    return Bridge(listener.info) if success else None

