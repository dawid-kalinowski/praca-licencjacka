Uruchamianie aplikacji:  

Instalujemy bazę danych w Dockerze za pomocą komendy opisanej w pliku `commands.txt`:  

`docker run -d --name mongodb -p 27017:27017 mongo:latest`

Wchodzimy w utworzony kontener w Dockerze, wchodzimy w bazę danych za pomocą komendy `mongo`, po czym wykonujemy wszystkie polecenia zapisane w pliku `db.txt`

W folderze głównym, po zainstalowaniu wszystkich wymaganych pakietów, uruchamiamy program main.py komendą `python3 main.py`

Aplikacja uruchamia się na porcie `127.0.0.1:5000`

