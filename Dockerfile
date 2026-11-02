FROM python-3.14


WORKDIR /app


COPY . .


RUN pip install fastapi uvicorn psycopg2-binary

CMD ["uvicorn","emailtest:app","--host","0,0,0,0","--port","8000"]
