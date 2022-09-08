FROM alpine:3.14
WORKDIR /squid

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Copy pip requirements file
ADD ./requirements.txt /squid/seat-bot/

# Download and install pip package
RUN pip install --upgrade pip
RUN pip install -r /squid/seat-bot/requirements.txt

#Copy file
ADD ./ /squid/seat-bot/

WORKDIR /squid/seat-bot
ENTRYPOINT python -u run.py