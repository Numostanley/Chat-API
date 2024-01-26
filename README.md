# Docker compose Installation

Clone the repository:

```
git clone https://github.com/Numostanley/Chat-API.git
```

Enter the root directory.
```
cd Chat-API
```

Run docker-compose

```
docker-compose up --build
```


# Manual Installation

Clone the repository:

```
git clone https://github.com/Numostanley/Chat-API.git
```

Enter the root directory.
```
cd Chat-API
```

Create a virtual environment.
```
python -m venv venv
```

Activate the virtual environment.

On Windows:
```
venv\Scripts\activate
```

On macOS and Linux:
```
source venv/bin/activate
```

Change the directory to the src folder:
```
cd src
```

Install dependencies:
```
pip install -r requirements/base.txt
```

### Database Setup

Make migrations:
```
python manage.py makemigrations
```

Apply migrations:
```
python manage.py migrate
```

Seed Clients:
```
python manage.py seed_clients
```

Running the Project
```
python manage.py runserver
```

# NOTE:
This project requires >= 3.8.
Ensure you have Redis and PostgreSQL properly installed and configured.
<br/>
You can also find the Postman API documentation 
to this project at: <br/>
https://www.postman.com/orange-capsule-84916/workspace/chat-api
