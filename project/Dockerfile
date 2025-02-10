FROM python:3.8.20
WORKDIR /app
COPY techtrends /app
RUN pip install -r requirements.txt 
RUN python3 init_db.py
EXPOSE 3111
CMD ["python", "app.py"]