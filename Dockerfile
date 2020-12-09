FROM centos:centos7.4.1708
MAINTAINER The CentOS Project <cloud-ops@centos.org>
ENV WHEEL_ARGS="-r requirements.txt"
RUN yum -y update
RUN yum -y install epel-release
RUN yum -y install python-pip
RUN yum -y install gcc python-devel libffi-devel openssl-devel libxml2-devel libxslt-devel make
RUN yum -y install git
RUN yum clean all
#RUN pip install --upgrade pip setuptools
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install no-manylinux1
RUN pip install wagon
WORKDIR /mnt
CMD ["sh", "-c", "wagon create --wheel-args=--no-cache-dir ${WHEEL_ARGS} -v -f -o ./ ./"]
