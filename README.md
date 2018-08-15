# ZipatoPy: Zipato Python API

The Python library to interact with Zipato smarthome controllers.

Inspired by [ggruner](https://github.com/ggruner/Zipatoapi).
Tested with Zipato Zipatile.

Main features:
* list devices, endpoints, attributes and attribute values
* manipulate virtual endpoints (create/get/set/delete)
* synchronization of Zipato controller
* local and cloud mode
* no external dependencies (build-in Python libs only)
* logging and verbose debug

TODO:
* add to PyPI repository
* integrate as [Home Assistant](https://www.home-assistant.io/) sensor

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Python Version

```
Python 2.7+
```

### Installation

From source:
```
git clone https://github.com/goooroooX/ZipatoPy.git
```

### Test run

Start with included samples:
* change USERNAME and PASSWORD to your my.zipato.com account information
* for test1.py change DEVICE, ENDPOINT and ATTRIBUTE

```
cd ZipatoPy/samples
python test1.py
python test2.py
```

API initialization for a cloud mode:
```
api = ZipatoPy(USERNAME, PASSWORD, verbose=True)
print(api.get_devices())
```

API initialization for a local mode:
```
api = ZipatoPy(USERNAME, PASSWORD, url='http://X.X.X.X:8080/zipato-web/v2/', verbose=True)
print(api.get_devices())
```
NOTE: local mode is limited comparing to cloud mode, but you will still be able to get attribute values when requesting directly with UUID.

## Authors

* **Dmitry Nikolaenya** - *code base* - [gooorooo.com](https://gooorooo.com)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details. 