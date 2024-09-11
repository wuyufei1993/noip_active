# noipactive

#### 介绍
noip定期激活

#### 说明
扫描邮箱中noip发送的激活提示邮件，自动激活noip DDNS


#### 安装教程
docker镜像见https://hub.docker.com/r/wuyufei1993/noipactive  

#### 环境变量
___SMTP_HOST___ 邮箱SMTP服务器地址，默认QQ邮箱smtp.qq.com  
___SMTP_SSL_PORT___ 邮箱SMTP服务器SSL端口，默认QQ邮箱465  
___IMAP_HOST___ 邮箱IMAP服务器地址，默认QQ邮箱imap.qq.com  
___IMAP_SSL_PORT___ 邮箱IMAP服务器SSL端口，默认QQ邮箱993  
___EMAIL_USERNAME___ 邮箱账号  
___EMAIL_PASSWORD___ 邮箱密码  
___NOIP_USERNAME___ NOIP账号  
___NOIP_PASSWORD___ NOIP密码  

#### 启动
QQ邮箱    
docker run -d --restart=always --name noipactive -e EMAIL_USERNAME="" -e EMAIL_PASSWORD="" -e NOIP_USERNAME="" -e NOIP_PASSWORD="" wuyufei1993/noipactive:latest    
其他邮箱需要配置SMTP服务器和IMAP服务器相关参数    
docker run -d --restart=always --name noipactive -e SMTP_HOST="" -e SMTP_SSL_PORT="" -e IMAP_HOST="" -e IMAP_SSL_PORT="" -e EMAIL_USERNAME="" -e EMAIL_PASSWORD="" -e NOIP_USERNAME="" -e NOIP_PASSWORD="" wuyufei1993/noipactive:latest


