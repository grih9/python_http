all: http_server.py

install: http_server.py
	sudo apt install python3
	useradd -c "DigitalAuthWeb user" -r -s /sbin/nologin -d /var/www/digitalauthweb digitalauthweb
	install -o root -g root -m 0755 http_server.py /usr/local/sbin
	mkdir -p /var/www/digitalauthweb
	mkdir -p /var/log/digitalauthweb
	cp -r webroot /var/www/digitalauthweb/
	chown -R digitalauthweb:digitalauthweb /var/www/digitalauthweb
	chown -R digitalauthweb:digitalauthweb /var/log/digitalauthweb
	install -o root -g root -m 0644 digitalauthweb.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl restart digitalauthweb.service

uninstall:
	sudo apt remove python3
	systemctl stop digitalauthweb
	rm -rf /var/www/digitalauthweb
	rm -rf /var/log/digitalauthweb
	rm -f /usr/local/sbin/http_server.py
	rm -f /etc/systemd/system/digitalauthweb.service
	systemctl daemon-reload
	userdel -f digitalauthweb
