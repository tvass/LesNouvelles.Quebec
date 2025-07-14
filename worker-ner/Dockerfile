# worker-ner/Dockerfile

FROM python:3.12-slim

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN useradd -m app \
    && mkdir -p /home/app/worker-ner /home/app/config /home/app/common \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app/worker-ner

COPY --chown=app:app worker-ner/requirements.txt /home/app/worker-ner/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app worker-ner /home/app/worker-ner
COPY --chown=app:app config /home/app/config
COPY --chown=app:app common /home/app/common

ENV PATH="/home/app/.local/bin:$PATH"

CMD ["python", "app.py"]
