# AioLocust

Note, that support of Python 2 is strictly prohibited for aiolocust.
Please, don't try to do anything that might at least theoretically leads us to support this version of the interpreter.
After 2nd attempt you will be lifetime banned for the contribution to OpenSource projects (we will follow you).

[![Build Status](https://api.travis-ci.org/kpidata/aiolocust.png)](http://travis-ci.org/kpidata/aiolocust) 

## Links

* Website: 
* Documentation: 

## Description

Aiolocust is an easy-to-use, distributed, user load testing tool. It is intended for load-testing web sites (or other systems) and
figuring out how many concurrent users a system can handle.

The idea is that during a test, a swarm of locusts will attack your website. The behavior of each locust (or test user if you will) is 
defined by you and the swarming process is monitored from a web UI in real-time. This will help you battle test and identify bottlenecks 
in your code before letting real users in.

Locust is completely event-based, and therefore it's possible to support thousands of concurrent users on a single machine.
In contrast to many other event-based apps it doesn't use callbacks. Instead it uses light-weight processes, through <a href="http://www.gevent.org/">gevent</a>.
Each locust swarming your site is actually running inside its own process (or greenlet, to be correct).
This allows you to write very expressive scenarios in Python without complicating your code with callbacks.


## Features

* Write user test scenarios in plain-old Python
* Distributed & Scalable - supports hundreds of thousands of users
* Web-based UI
* Can test any system
* Hackable


## Documentation

More info and documentation can be found at: 


## Authors

* Viacheslav Kakovskyi (@kakovskyi)
* Behersky Misha (@bmwant)

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).


## Supported Python Versions

Aiolocust support *only* Python 3.5

