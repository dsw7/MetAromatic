FROM debian

RUN apt-get update && \
    apt-get install -y \
    git \
    make \
    python3 \
    python3-pip

CMD git clone --single-branch --branch working https://github.com/dsw7/MetAromatic.git && \
    cd MetAromatic && \
    make full
