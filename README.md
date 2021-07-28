# aminer-akafka

This daemon polls logs from kafka topics and writes it to a unix-domain-socket(for [logdata-anomaly-miner](https://github.com/ait-aecid/logdata-anomaly-miner.git))

**please note that this project is  work in progress**

# Installation

```
sudo make install
```

After that set owner of /var/lib/akafka to aminer-user:

```
sudo chown aminer:aminer /var/lib/akafka
```

# Configuration

It is possible to configure akafka via configuration file which must be located at '/etc/aminer/kafka.conf' or via environment variables. 
A sample of the configuration file can be found at [etc/kafka.conf](/etc/kafka.conf)
The following environment variables are available:

| Environment variable | Example | Description |
| -------------------- | ------- | ----------- |
| KAFKA_TOPICS         | `['aminer','logs']` | List of topics |
| AKAFKA_UNIXPATH      | /var/lib/akafka/aminer.sock | Path to the unix domain socket |
| KAFKA_BOOTSTRAP_SERVERS | localhost:9092 | Kafka server and port |
| AKAFKA_FILTERS       | `['.*phy_payload.*tx_info.*frequency.*rx_info.*gateway_id.*','.*example.com.*']` | List of regex filters |

# Poll manually

```
sudo /usr/local/bin/akafkad.py
```

# Starting the daemon

```
sudo systemctl enable akafkad
sudo systemctl start akafkad
```

# Testing

Normally the daemon starts polling the elasticsearch as soon as some other programm reads from the unix-domain-socket.
It is possible to read from the socket manually using ncat(from nmap) as follows:

```
sudo ncat -U /var/lib/aminer/aminer.sock
```

# Uninstall

The following command will uninstall akafka but keeps the configuration file:
```
sudo make uninstall
```
