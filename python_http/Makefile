all: http_server.py

install: http_server.py
	useradd -c "DigitalAuthWeb user" -r -s /sbin/nologin -d /var/www/digitalauthweb digitalauthweb
	install -o root -g root -m 0755 http_server.py /usr/local/sbin
	install -o root -g root -m 0755 tcp_server.py /usr/local/sbin
	install -o root -g root -m 0755 settings.py /usr/local/sbin
	sudo apt install apache2-utils
	htdigest -c /usr/local/sbin/.htdigest admin admin
	htdigest /usr/local/sbin/.htdigest auth admin
	htdigest /usr/local/sbin/.htdigest auth user
	mkdir -p /var/www/digitalauthweb
	mkdir -p /var/log/digitalauthweb
	cp -r webroot /var/www/digitalauthweb/
	chown -R digitalauthweb:digitalauthweb /var/www/digitalauthweb
	chown -R digitalauthweb:digitalauthweb /var/log/digitalauthweb
	install -o root -g root -m 0644 digitalauthweb.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl restart digitalauthweb.service

uninstall:
	systemctl stop digitalauthweb
	rm -rf /var/www/digitalauthweb
	rm -rf /var/log/digitalauthweb
	rm -f /usr/local/sbin/http_server.py
	rm -f /usr/local/sbin/tcp_server.py
	rm -f /usr/local/sbin/.htdigest
	rm -f /etc/systemd/system/digitalauthweb.service
	systemctl daemon-reload
	userdel -f digitalauthweb
