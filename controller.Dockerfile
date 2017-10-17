FROM centos:7
LABEL authors="Chen Leji<chenleji@wise2c.com>"

RUN yum install -y epel-release \
    && yum install -y --setopt=tsflags=nodocs python-pip \
    && yum install --setopt=tsflags=nodocs --assumeyes inet-tools gcc python-devel wget git 

COPY ./kuryr-rancher-controller.sh /
COPY . /opt/kuryr-rancher

RUN cd /opt/kuryr-rancher \
    && pip install --no-cache-dir . \
    && rm -fr .git \
    && yum -y history undo last \
    && groupadd -r kuryr -g 711 \
    && useradd -u 711 -g kuryr \
         -d /opt/kuryr-rancher \
         -s /sbin/nologin \
         -c "Kuryr controller user" \
         kuryr \
    && chown kuryr:kuryr /opt/kuryr-rancher \
    && touch /etc/kuryr.conf \
    && chmod 777 /kuryr-rancher-controller.sh

USER kuryr

ENTRYPOINT [ "/kuryr-rancher-controller.sh" ]

#CMD ["--config-dir", "/etc/kuryr"]
#ENTRYPOINT [ "/usr/bin/kuryr-rancher-controller" ]
