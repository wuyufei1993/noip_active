FROM wuyufei1993/chrome_for_testing:136.0.7103.94
WORKDIR /opt
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-updates main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://security.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse' >> /etc/apt/sources.list
RUN apt update
ADD active_noip.py /opt/
ADD run.sh /opt/
ENV TZ=Asia/Shanghai
ENV SMTP_HOST 'smtp.qq.com'
ENV SMTP_SSL_PORT 465
ENV IMAP_HOST 'imap.qq.com'
ENV IMAP_SSL_PORT 993
ENV EMAIL_USERNAME ''
ENV EMAIL_PASSWORD ''
ENV NOIP_USERNAME ''
ENV NOIP_PASSWORD ''
CMD /opt/run.sh
