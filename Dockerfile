FROM python:3.10.4


WORKDIR /usr/src/app

# This will copy to app directory above
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code to app dir
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]