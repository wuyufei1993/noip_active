FROM wuyufei1993/chrome_for_testing:136.0.7103.94
WORKDIR /opt
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
