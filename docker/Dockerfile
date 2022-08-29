FROM --platform=alpine/amd64 ubuntu:3.14
WORKDIR /pecom

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

# Install ssh, git, pip, venv, sshpass, nano
RUN apt update && \
    apt-get -y install python3-pip python3.9-dev python3.9-venv

# Copy pip requirements file
ADD ./requirements.txt /seat_notification_bot/

# Download and install pip package
RUN pip install --upgrade pip
RUN pip install -r /seat_notification_bot/requirements.txt

#Copy file
ADD ./ /seat_notification_bot/

WORKDIR /seat_notification_bot
ENTRYPOINT python -u run.py