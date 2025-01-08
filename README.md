Uruchamianie aplikacji:  

Instalujemy bazę danych w dockerze za pomocą komendy opisanej w pliku `commands.txt`:  

`docker run -d --name mysql-base -e MYSQL_ROOT_PASSWORD=123 -p 3306:3306 mysql:latest --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`

W folderze głównym, po zainstalowaniu wszystkich wymaganych pakietów, uruchamiamy program app.py komendą `python3 app.py`

Aplikacja uruchamia się na porcie `5050`

