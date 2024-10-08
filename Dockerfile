FROM python:3.9
RUN chmod 777 -R /root
WORKDIR /
#RUN chmod 777 -R /
#pweas
ENV STATUS_CUSTOM_ROOT_PATH=/Status
RUN apt update -y && apt upgrade -y
RUN apt-get install -y nodejs npm
RUN apt install python3 -y && apt install python3-pip -y
RUN pip3 install flask --break-system-packages
RUN pip install requests cachetools flask
COPY . .
EXPOSE 7860
CMD ["python3", "app.py"]
