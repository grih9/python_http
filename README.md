# python_http

Представляет из себя системную службу digitalauthweb.

Порт по умолчанию 8050. 

Папка:
>/var/www/digitalauthweb/webroot.

Запуск службы:
> sudo make install

После запуска предлагает ввести три пароля для пользователей по умолчанию:
* для admin с правом доступа admin
* для admin с правом доступа auth
* для user с правом доступа auth

Журналирование:
> /var/log/digitalauthweb/digitalauthweb.log

Создание обычного (право доступа auth) нового пользователя:
>htdigest /usr/local/sbin/.htdigest auth <имя пользователя>

Создание нового администратора (для правильной работы кроме admin доступно только имя root)
>htdigest /usr/local/sbin/.htdigest admin root \
>htdigest /usr/local/sbin/.htdigest auth root

Выключение службы:
>sudo make uninstall

Ресурсы доступные без авторизации:
- "/index.html"
- "/picture.png"

Ресурсы доступные после авторизации (право доступа auth):
- "/private"
- "/private/index.html"
- "/private/picture.png"
- "/secret"

Если пользователь сразу авторизовался с правом доступа admin, 
то он может посещать все страницы без дополнительной авторизации.

Если пользователь сразу авторизовался с правом доступа auth, но также
имеет право доступа admin, то при переходе в ресурс доступный для admin, он может ввести соответствующий пароль.
Если такого права доступа нет, то пользователь получает сообщение о недоступности данного ресурса с имеющимися правами.

Ресурсы доступные только для admin (право доступа admin):
- "/admin"
- "/super_secret"
- "/private/admin"
- "/private/admin/index.html"
- "/private/admin/picture.png"