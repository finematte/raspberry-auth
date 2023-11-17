# Raspberry WiFi Configurator

More advance version which shuts down hotspot and Django server after establishing WiFi connection.

## Deployment

To deploy this project first install:

```bash
  sudo apt-get install hostapd
  sudo apt-get install dnsmasq
```

Then install requirements:

```bash
  sudo pip install -r requirements.txt
```

For website testing run:

```bash
  sudo python3 manage.py runserver 0.0.0.0:8000
```

To run hotspot configurator and deploy Django website:

```bash
  sudo python3 hotspot.py start
```

To stop the hotspot and revert all changes (hostapd, dnsmasq, dhcpcd configuration files):

```bash
  sudo python3 hotspot.py stop
```

To reset/disconnect from WiFi use:

```bash
  sudo python3 hotspot.py reset
```

After establishing internet connection it should be persistant after the reboot.
