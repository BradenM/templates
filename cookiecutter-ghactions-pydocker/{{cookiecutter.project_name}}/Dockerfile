FROM python:{{ cookiecutter.python_version }}

RUN pip install {% for dep, ver in cookiecutter.requirements | items %}{{ dep }}{{ ver }} {% endfor %}

COPY ./app /app

CMD ["python", "/app/main.py"]
