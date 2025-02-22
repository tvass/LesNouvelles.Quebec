# backend/Dockerfile

FROM python:3.12-slim

RUN useradd -m app \
    && mkdir -p /home/app/backend /home/app/config /home/app/common \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app/backend

COPY --chown=app:app backend/requirements.txt /home/app/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code spécifique au backend
COPY --chown=app:app backend /home/app/backend

# Copier les répertoires config et common depuis le contexte global
COPY --chown=app:app config /home/app/config
COPY --chown=app:app common /home/app/common

ENV PATH="/home/app/.local/bin:$PATH"

EXPOSE 5000
CMD ["python", "app.py"]
