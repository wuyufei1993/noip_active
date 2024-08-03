FROM ubuntu:24.10
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-updates main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb http://security.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse' >> /etc/apt/sources.list
RUN apt update && apt -y install python3 python3-selenium
ADD ./google-chrome-stable/google-chrome-stable_current_amd64.deb /
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y
RUN rm -rf /google-chrome-stable_current_amd64.deb
ADD chromedriver-linux64/ /opt/chromedriver-linux64/
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
