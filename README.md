# Philips Hue Lighting System - Utilities

This repository has some utilities to query and monitor a hue lighting system.

It uses zeroconf to locate the bridge - if your app can find the bridge on your network, then these
utilties will as well.

You can read about Hue [here](https://www.philips-hue.com/).


## Getting Started

This section describes how to get started with listening for events.

Setup python environment:

    python3 -m venv pyenv
    source pyenv/bin/activate
    pip3 install -r requirements.txt

Register an application and create configuration:

    ./bin/init-application.py [-n <app-name>] [-i <app-instance>]

This creates a configuration file in the `hlib.resources` directory that the other tools automatically find and use.
It uses a default application name with unique instance name if not provided.


## Utilities

| Utility           | Description                                                       |
| ----------------- | ----------------------------------------------------------------- |
| bridge-info.py    | find your bridge and pring some info about it                     |
| ls-devices.py     | list all devices attached to your bridge                          |
| ls-light.py       | print full configuration of the light                             |
| ls-resource.py    | print information about any type of resource                      |
| event-syslog.py   | log events to the system syslog facility                          |
| event-influxdb.py | log to an influxdb database                                       |
| read-temp.py      | reads the temperature from a devices that records temperature     |
| silent-light.py   | attempts to configure your light to stay off after a power outage |
| check-silent.py   | verify lights are configured to be silent; pushover notification  |

### Bridge Info

This one is very simple. You don't need this info to run any of the other utilities, but if you're curious:

    $ ./bin/bridge-info.py 
    Bridge:
     Hostname: XXXXXXXXXXXXXXXX.local.
           ID: XXXXXXXXXXXXXXXX
        Model: BSB002
    Addresses: 192.168.1.111
         Port: 443

If you don't get a response but the app on your mobile device works, it's probably your firewall blocking
the response. 

### List Devices

This prints out all the devices on your bridge and the services they offer:

    $ ./bin/ls-devices.py
    
    Product: Hue ambiance candle
      Model: LTW012
       Name: Lamp 1
         ID: cacca7ff-5660-4379-929d-f435f94ee99c
    Services:
      - zigbee_connectivity
        abf90a95-f0f9-429b-a282-3c89dfd4ba7b
      - light
        f702d8e5-9233-4160-95d7-28c4b924331e
      - taurus_7455
        bbdd254f-f4b2-4729-a3d5-f4a3da0cbaf9
        
    Product: Hue white lamp
      Model: LWB010
       Name: Backdoor
         ID: f333430c-1775-496b-9d41-f6246f92e079
    Services:
      - zigbee_connectivity
        f65f92e4-0473-4d60-89fc-bf72970c6cc6
      - light
        7d12ae2a-dad7-4564-833c-386f4b3f0e57
      - taurus_7455
        2c4b1320-22d9-4bad-9fa7-298bd17927ac
        

### List Light

This lists details of a light. Used the UUID from the light service listed in ls-devices.

    $ ./bin/ls-light.py 7d12ae2a-dad7-4564-833c-386f4b3f0e57
    {'alert': {'action_values': ['breathe']},
     'color_temperature': {'mirek': 443,
                           'mirek_schema': {'mirek_maximum': 454,
                                            'mirek_minimum': 153},
                           'mirek_valid': True},
     'color_temperature_delta': {},
     'dimming': {'brightness': 0.0, 'min_dim_level': 2.0},
     'dimming_delta': {},
     'dynamics': {'speed': 0.0,
                  'speed_valid': False,
                  'status': 'none',
                  'status_values': ['none']},
     'effects': {'effect_values': ['no_effect', 'candle'],
                 'status': 'no_effect',
                 'status_values': ['no_effect', 'candle']},
     'id': '5fa16ad4-843e-41b4-bae6-4329a45f1f76',
     'id_v1': '/lights/7',
     'identify': {},
     'metadata': {'archetype': 'table_shade', 'name': 'Kitchen'},
     'mode': 'normal',
     'on': {'on': False},
     'owner': {'rid': 'a08b0c33-9718-4cec-ad0e-2d7a25464064', 'rtype': 'device'},
     'powerup': {'color': {'color_temperature': {'mirek': 439},
                           'mode': 'color_temperature'},
                 'configured': True,
                 'dimming': {'dimming': {'brightness': 49.01}, 'mode': 'dimming'},
                 'on': {'mode': 'on', 'on': {'on': True}},
                 'preset': 'custom'},
     'signaling': {'signal_values': ['no_signal', 'on_off']},
     'type': 'light'}


## Syslog Logger

To run the syslogger, use this command:

    $ ./event-syslog.py motion temperature light_level

Depending on the setup of your rsyslog, this will write events to `/var/log/syslog` or whatever
is the default on your system. See the next sections for different logging options.

### Forwarding Logs to Remote System

To configure the local system to forward `local0` events to a remote system, edit the configuration file
`/etc/rsyslog.conf` and add the line below, changing the `X.X.X.X` to the IP address of the remote system:

    local0.*  action(type="omfwd" target="X.X.X.X" port="514" protocol="udp"
                action.resumeRetryCount="100"
                queue.type="linkedList" queue.size="10000")

Then update the default entry to not log any `local0` events to the default syslog file:

    *.*;auth,authpriv,local0.none   -/var/log/syslog

Restart and the events will be forwarded:

    systemctl restart rsyslog

You can then setup logging on the remote system as in the section below.

###  Logging to Separate File

There are two configuration changes that need to be made:

1. direct `local0` facility events to their own log file
2. stop `local0` events being sent to the default log file

Edit the file `/etc/rsyslog.conf` and add the first line below and make the
changes to the second line:

    local0.*                        /var/log/hue-events.log
    *.*;auth,authpriv,local0.none   -/var/log/syslog

Restart `rsyslog` and all should work:

    systemctl restart rsyslog


### Log Rotation

To setup log rotation, edit the file `/etc/logrotate.d/rsyslog` and add the file
`/var/log/hue-events.log` to the list of log files to rotate - just make it match all
the others.

I don't think the service needs to be restarted as it is run periodically on a timer,
but if you want to:

    systemctl restart logrotate


## InfluxDB Logger

To log to an InfluxDB, you need to setup the account and permissions as environment variables and 

    export IDB_TOKEN="influxdb-access-token"
    export IDB_ORG="influxdb-org-name"
    export IDB_BUCKET="influxdb-bucket-to-log-to"
    export IDB_URL="http://<your-influxdb-host>:8086"

    ./bin/event-influxdb.py motion temperature light_level

The logger currently only logs 'temperature', 'light_level' and 'motion' events. There's no reason why
other events can't be logged, I was just interested in these ones so didn't bother adding support for 
other event types or even better, generalizing the code to handle any event type. On the todo list.

Information about InfluxDB can be found [here](https://docs.influxdata.com/influxdb/v2.6/get-started/).
To install OpenSource InfluxDB 2.x, follow the instructions on their download portal
[here](https://portal.influxdata.com/downloads/).


## Silent Light

I've had a few issues after power outages where the lights come on. This is normally OK except for when 
it happens in the middle of the night in the bedroom. From memory, there used to be a setting accessible 
from the app to control this, but I can't find it anymore. There is an option still available in the API 
though which this utility uses to configure the option.

It works in a lot of situations I've tested, however, if the power if off for an extended period of time, 
then they still come on with the power.

Once you have the light's id from the 'ls-devices.py' tool, you can run it like this:

    $ ./bin/silent-light.py 7d12ae2a-dad7-4564-833c-386f4b3f0e57

Listing the light's settings once this has been run will show the powerup configuration to be off:

    $ ./bin/ls-light.py 7d12ae2a-dad7-4564-833c-386f4b3f0e57
    {...
     'powerup': {'color': {'mode': 'previous'},
                 'configured': True,
                 'dimming': {'mode': 'previous'},
                 'on': {'mode': 'on', 'on': {'on': False}},
                 'preset': 'custom'},
      ... }

Test it by unplugging, waiting a few minutes and then plugging back in.

To do the opposite, that is have the light always turn on, run with the '--negate' flag.

### Checking Silent Status

To verify that your lights are still in silent mode, you can use the check-silent.py application:

    $ ./check-silent.py -h
    usage: check-silent.py [-h] light_id [light_id ...]
    
    positional arguments:
      light_id    id of light to check

For example:

    $ ./check-silent.py fc513d4a-2b9b-4cc5-b0a7-38e4812949a1 c8dba9da-9b15-44f0-8888-0a4a72c3620a
    fc513d4a-2b9b-4cc5-b0a7-38e4812949a1: name: Light1, silent: True
    c8dba9da-9b15-44f0-8888-0a4a72c3620a: name: Light2, silent: True

This can also optionally send notifications to you using the pushover APP. To configure this, edit the configuration file
in 'hlib/resources/config.yaml' and add these entries:

    pushover_token: application-token
    pushover_clients:
    - client-key

To create your application and find your client key, refer to the [pushover API documentation](https://pushover.net/api).

I run this as a cron job on a raspberry pi.

