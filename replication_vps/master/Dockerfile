FROM python:3.10.13

WORKDIR /home
COPY app.py .
COPY requirements.txt .

RUN pip install -r requirements.txt
CMD ["python3", "-m", "flask", "--app", "app.py", "run", "--host=185.189.12.171"]