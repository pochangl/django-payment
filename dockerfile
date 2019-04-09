From python:3.6

RUN pip install django==1.11.13
RUN mysqlclient==1.3.9

RUN mkdir /mnt/server
RUN mkdir /mnt/payment

RUN echo '' > /test.sh

WORKDIR /
CMD /test.sh