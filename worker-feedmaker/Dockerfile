# worker-feedmaker/Dockerfile

FROM python:3.12-slim

RUN useradd -m app \
    && mkdir -p /home/app/worker-feedmaker /home/app/config /home/app/common \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app/worker-feedmaker

COPY --chown=app:app worker-feedmaker/requirements.txt /home/app/worker-feedmaker/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app worker-feedmaker /home/app/worker-feedmaker
COPY --chown=app:app config /home/app/config
COPY --chown=app:app common /home/app/common

ENV PATH="/home/app/.local/bin:$PATH"

CMD ["python", "app.py"]
