FROM python:2.7
MAINTAINER cjonesy

RUN mkdir /var/model && \
    wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 \
         -O /var/model/shape_predictor_68_face_landmarks.dat.bz2 && \
    bzip2 -d /var/model/shape_predictor_68_face_landmarks.dat.bz2 && \
    apt update && apt install -y cmake libboost-python-dev

COPY . /opt/faceswap_bot

RUN pip install -r /opt/faceswap_bot/requirements.txt

ENTRYPOINT ["python"]

CMD ["/opt/faceswap_bot/faceswap_bot/cli.py"]
