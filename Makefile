init:
	pip3 install -r requirements.txt

install: init
	test -d /usr/lib/akafka || mkdir -p /usr/lib/akafka
	cp -r akafka/* /usr/lib/akafka/
	test -d /etc/aminer/ || mkdir /etc/aminer/
	test -e /etc/aminer/kafka.conf || cp etc/kafka.conf /etc/aminer/kafka.conf
	test -d /etc/systemd/system && cp etc/akafkad.service /etc/systemd/system/akafkad.service
	test -d /var/lib/akafka || mkdir /var/lib/akafka
	cp bin/akafkad.py /usr/lib/akafka/akafkad.py
	chmod 755 /usr/lib/akafka/akafkad.py
	test -e /usr/local/bin/akafkad.py || ln -s /usr/lib/akafka/akafkad.py /usr/local/bin/akafkad.py

uninstall:
	rm -rf /usr/lib/akafka
	unlink /usr/local/bin/akafkad.py
