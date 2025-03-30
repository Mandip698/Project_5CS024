->> Clone repository

```bash
git clone https://github.com/Mandip698/Project_5CS024.git
```

->> Create a Virtual environment using

```bash
python -m venv env
```

->> Activate Virtual environment using

-> For Windows

```bash
env\Scripts\activate
```

-> For Mac/Linux

```bash
source env\bin\activate
```

->> Install all requirements using

```bash
pip install -r requirements.txt
```

->> Initialize models using

```bash
python manage.py makemigrations
python manage.py migrate
```

->> Create admin user using

```bash
python manage.py createsuperuser
```

->> Start Web App using

```bash
python manage.py runserver
```
