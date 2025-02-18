FROM python:3.12-slim
RUN useradd -m app
RUN mkdir /app && chown app:app /app
USER app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PATH="/home/app/.local/bin:$PATH"
EXPOSE 5000
CMD ["python", "app.py"]