# frontend/Dockerfile

FROM python:3.12-slim

RUN useradd -m app \
    && mkdir -p /home/app/fronted /home/app/config /home/app/common \
    && chown -R app:app /home/app

USER app
WORKDIR /home/app/frontend

COPY --chown=app:app frontend/requirements.txt /home/app/frontend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app frontend /home/app/frontend

# Copier les répertoires config et common depuis le contexte global
COPY --chown=app:app config /home/app/config
COPY --chown=app:app common /home/app/common

ENV PATH="/home/app/.local/bin:$PATH"

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]