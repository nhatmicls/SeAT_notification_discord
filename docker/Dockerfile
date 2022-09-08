FROM --platform=linux/amd64 ubuntu:20.04
WORKDIR /squid

# Install python3.9
RUN apt update && \
    apt -y install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt -y install python3.9 && \
    apt -y install libcairo2-dev

# Set default python3.9
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install pip, venv
RUN apt update && \
    apt-get -y install python3-pip python3.9-dev python3.9-venv

# Copy pip requirements file
ADD ./requirements.txt /squid/seat-bot/

# Download and install pip package
RUN pip install --upgrade pip
RUN pip install -r /squid/seat-bot/requirements.txt

#Copy file
ADD ./ /squid/seat-bot/

WORKDIR /squid/seat-bot
ENTRYPOINT python -u run.py