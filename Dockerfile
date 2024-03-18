FROM python:3.12-slim

LABEL "maintainer" "Jan Zizka jan.zizka@datamole.cz>"
LABEL "repository" "https://github.com/datamole-ai/jfrog-oidc-change"
LABEL "homepage" "https://github.com/datamole-ai/jfrog-oidc-change"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PIP_NO_CACHE_DIR 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_ROOT_USER_ACTION ignore

ENV PYTHONPATH "/root/.local/lib/python3.12/site-packages"

WORKDIR /app
COPY oidc-exchange.py .
COPY requirements.txt .

RUN pip install --user --upgrade --no-cache-dir -r requirements.txt

RUN chmod +x oidc-exchange.py
ENTRYPOINT ["python3", "-u", "/app/oidc-exchange.py"]
