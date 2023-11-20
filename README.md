# Philips Hue Lighting System - Utilities

This repository has some utilities to help configure and monitor a hue lighting system. Apart from getting general information
about your bridge and devices, it has tools to:

* configure lights to remain off on poweron no matter what
* monitor the system for events and optionally log to an influxdb database

The system uses zeroconf to locate the bridge - if your app can find the bridge on your network, then these
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

| Utility         | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| bridge-info.py  | find your bridge and pring some info about it                    |
| ls-devices.py   | list all devices attached to your bridge                         |
| ls-light.py     | print full configuration of the light                            |
| silent-light.py | configure your light to stay off when the power comes back on    |
| check-silent.py | verify lights are configured to be silent; pushover notification |

### Bridge Info

This one is very simple. You don't need this info to run any of the other utilities, but if you're curious:

    $ ./bin/bridge-info.py 
    Bridge:
     Hostname: XXXXXXXXXXXXXXXX.local.
           ID: XXXXXXXXXXXXXXXX
        Model: BSB002
    Addresses: 192.168.1.111
         Port: 443


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


### Silent Light

It seems that the hue app developers have removed the option of forcing the light to remain off when the power comes 
on from the iOS app. Not sure why, but after being woken up a few times in the middle of the night, I have concluded 
that this is pretty important.

Thankfully the 'stay off when the power comes back on no matter what' configuration seems to still be accessible at the 
API level - this utility sets it for the light you specify.

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

Note that this has worked correctly in all the testing I have done, but it's possible there is some scenario
that I haven't thought of where this doesn't work. Seems pretty solid though.

Also, it could be possible for a software update to overwrite this setting, so you'll need to keep an eye on it.

Enjoy your slumber!

### Checking Silent Status

To verify that your lights are still in silent mode, you can use the check-silent.py application:

    $ ./check-silent.py -h
    usage: check-silent.py [-h] light_id [light_id ...]
    
    positional arguments:
      light_id    id of light to check

For example:

    $ ./check-silent.py fc513d4a-2b9b-4cc5-b0a7-38e4812949a1 c8dba9da-9b15-44f0-8888-0a4a72c3620a
    fc513d4a-2b9b-4cc5-b0a7-38e4812949a1: name: Light1, configured: True
    c8dba9da-9b15-44f0-8888-0a4a72c3620a: name: Light2, configured: True

This can also optionally send notifications to you using the pushover APP. To configure this, edit the configuration file
in 'hlib/resources/config.yaml' and add these entries:

    pushover_token: application-token
    pushover_clients:
    - client-key

To create your application and find your client key, refer to the [pushover API documentation](https://pushover.net/api).

I run this as a cron job on a raspberry pi.

## Event Listener

The event listener uses the event stream interface on the bridge. To listen to all events, run
this:

    ./bin/event-listener.py

To filter the events so you only see motion and temperature events, run the command like this:

    ./bin/event-listener.py motion temperature
  
This checks the 'type' field in the event data for an exact match. If you run the listener for a while
with no filter and you will see the range that's possible.


## Logging Events To InfluxDB

The utility `event-logger.py` can be used with `event-listener.py` to log events to an InfluxDB database.

Information about InfluxDB can be found [here](https://docs.influxdata.com/influxdb/v2.6/get-started/).
To install OpenSource InfluxDB 2.x, follow the instructions on their download portal
[here](https://portal.influxdata.com/downloads/).

The utility `event-logger.py` uses the InfluxData python client library. You can read about
it [here](https://docs.influxdata.com/influxdb/v2.0/api-guide/client-libraries/python/).

To run the event capture with logging, run a command like this:

    export IDB_TOKEN="influxdb-access-token"
    export IDB_ORG="influxdb-org-name"
    export IDB_BUCKET="influxdb-bucket-to-log-to"
    export IDB_URL="http://<your-influxdb-host>:8086"

    ./bin/event-listener.py temperature motion light_level | ./bin/event-logger.py

You'll start seeing events arriving in InfluxDB.

The logger currently only logs 'temperature', 'light_level' and 'motion' events. There's no reason why
other events can't be logged, I was just interested in these ones so didn't bother adding support for 
other event types or even better, generalizing the code to handle any event type. On the todo list.


