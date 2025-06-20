Uruchamianie aplikacji:  

Instalujemy bazę danych w Dockerze za pomocą komendy opisanej w pliku `commands.txt`:  

`docker run -d --name mongodb -p 27017:27017 mongo:latest`
W przypadku, gdy na komputerze port 27017 jest zajęty, można użyć dowolnego innego, wtedy polecenie będzie wyglądało następująco:

`docker run -d --name mongodb -p xxxx:27017 mongo:latest`, ale zamiast xxxx wpisać docelowy port

Wchodzimy w utworzony kontener w Dockerze, wchodzimy w bazę danych za pomocą komendy `mongosh`, po czym wykonujemy wszystkie polecenia zapisane w sekcji `---DB---` pliku `commands.txt`

Instalujemy wszystkie pakiety potrzebne do uruchomienia apliakcji:
`pip install flask flask-cors flask-pymongo pymongo python-dotenv joblib flask-socketio`

Należy stworzyć plik .env i uzupełnić danymi

```
MONGO_URI=mongodb://localhost:27017/word_db
PORT_APP= 
```

W przypadku, gdy baza została uruchomiona na innym porcie niż 27017, należy to zmienić na ten port.

W folderze głównym uruchamiamy program main.py komendą `python3 main.py`

Aplikacja uruchamia się na porcie `127.0.0.1:PORT_APP`, zamiast PORT_APP należy wpisać port, który będzie podany w pliku .env

