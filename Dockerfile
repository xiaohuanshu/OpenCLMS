FROM python:2

WORKDIR /usr/src/app

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_12_1

COPY zhengfang/instantclient/* /tmp/

RUN \
    apt-get update && apt-get install -y unzip libaio1 && rm -rf /var/lib/apt/lists/* && \
    unzip "/tmp/instantclient*.zip" -d /opt/oracle

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .