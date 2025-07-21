from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import smtplib
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from datetime import timedelta
from time import sleep

login_url = 'https://www.noip.com/login'
login_success_url = 'https://my.noip.com/'
dynamic_dns_url = "https://my.noip.com/dynamic-dns"
noip_username = os.getenv("NOIP_USERNAME")
noip_password = os.getenv("NOIP_PASSWORD")
smtp_host = os.getenv("SMTP_HOST")
smtp_ssl_port = int(os.getenv("SMTP_SSL_PORT", '465'))
imap_host = os.getenv("IMAP_HOST")
imap_ssl_port = int(os.getenv("IMAP_SSL_PORT", '993'))
email_username = os.getenv("EMAIL_USERNAME")
email_password = os.getenv("EMAIL_PASSWORD")
active_email_title = 'ACTION REQUIRED'
valid_code_email_title = 'No-IP Verification Code:'

if os.name == 'nt':
    driver_path = r'chromedriver-win64/chromedriver.exe'
    last_active_date_file = r'active_date'
else:
    driver_path = r'/opt/chromedriver-linux64/chromedriver'
    last_active_date_file = r'/opt/active_date'


def read_last_active_date():
    try:
        with open(last_active_date_file, 'r') as file:
            last_active_date = file.read()
        return last_active_date
    except FileNotFoundError:
        return None


def write_last_active_date():
    with open(last_active_date_file, 'w') as file:
        file.write(datetime.now().strftime("%Y-%m-%d"))


def is_need_run_task():
    last_active_date = read_last_active_date()
    if last_active_date is None or last_active_date == '':
        return True
    current_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if current_date > last_active_date:
        return True
    else:
        return False


def email_server():
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_ssl_port)
        mail.login(email_username, email_password)
        # 选择邮箱文件夹
        mail.select('INBOX')
        return mail
    except Exception:
        print('email server login fail, check email account/config')
        return None


# 搜索邮件 获取最新一封
def search_email(mail_server, title):
    date_str = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    # 搜索邮件
    status, msg_nums = mail_server.search(None, 'SINCE', date_str, 'SUBJECT', title)
    nums = msg_nums[0].split()
    if len(nums) == 0:
        return None
    else:
        status, email_data = mail_server.fetch(nums[len(nums) - 1], '(RFC822)')
        return email.message_from_bytes(email_data[0][1])


# 获取邮件标题
def get_subject(msg):
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        if encoding:
            subject = subject.decode(encoding)
        else:
            subject = subject.decode('utf-8')
    return subject


def read_valid_code(mail):
    code_mail = search_email(mail, valid_code_email_title)
    if code_mail is None:
        return None
    mail_title = get_subject(code_mail)
    valid_code = mail_title.replace(valid_code_email_title, '').strip()
    return valid_code


def check_email(mail):
    active_mail = search_email(mail, active_email_title)
    if active_mail is None:
        return
    else:
        active_noip(mail, 0)


def process_locale_mismatch_modal(driver):
    modal = driver.find_element(value='mismatchLanguageModal')
    if modal is not None:
        is_hidden = modal.get_dom_attribute("aria-hidden")
        if is_hidden == 'false':
            cancel_button = driver.find_element(value='modalLocaleMismatchDismissed')
            cancel_button.click()
            sleep(1)


def login(driver, mail, actions):
    driver.get(login_url)
    driver.implicitly_wait(60)
    sleep(3)
    username_input = driver.find_element(value='username')
    if username_input is not None:
        username_input.click()
        if username_input.text is None or username_input.text == '':
            username_input.send_keys(noip_username)

    password_input = driver.find_element(value='password')
    if password_input is not None:
        password_input.click()
        password_input.send_keys(noip_password)

    submit_button = driver.find_element(value='clogs-captcha-button')
    if submit_button is not None:
        actions.move_to_element(submit_button).perform()
        submit_button.click()
        driver.implicitly_wait(60)
        sleep(3)
    print(f'chrome browser current url {driver.current_url}')
    if driver.current_url == login_success_url:
        return
    elif driver.current_url == 'https://www.noip.com/2fa/verify':
        print('login need email verify')
        driver.implicitly_wait(60)
        sleep(60)
        valid_code = read_valid_code(mail)
        while valid_code is None:
            sleep(10)
            valid_code = read_valid_code(mail)
        opt_input = driver.find_element(value='otp-input')
        valid_code_inputs = opt_input.find_elements(By.TAG_NAME, 'input')
        for index, valid_code_input in enumerate(valid_code_inputs):
            actions.move_to_element(valid_code_input).perform()
            valid_code_input.click()
            valid_code_input.send_keys(valid_code[index])

        verify_button = driver.find_element(By.NAME, 'submit')
        if verify_button is not None:
            verify_button.click()
            return


def active_dynamic_host(driver):
    process_locale_mismatch_modal(driver)
    dynamic_dns_url_num = 0
    success = False
    active_flag = False
    while True:
        driver.get(dynamic_dns_url)
        dynamic_dns_url_num = dynamic_dns_url_num + 1
        driver.implicitly_wait(60)
        if driver.current_url == dynamic_dns_url:
            break
        if dynamic_dns_url_num < 20:
            print(f'Failed to redirect to activation page, current URL: {driver.current_url}, failed attempts: {dynamic_dns_url_num}.')
        else:
            print(f'Failed to redirect to activation page, current URL: {driver.current_url}, failed attempts: {dynamic_dns_url_num}, activation stopped!')
            return success, active_flag

    # 等待列表数据加载，数据由异步请求加载
    sleep(120)
    div_element = driver.find_element(value='host-panel')
    # 判断是否为激活状态
    a_web_elements = div_element.find_elements(By.TAG_NAME, 'a')
    for a_web_element in a_web_elements:
        if a_web_element is None or not a_web_element.text:
            continue
        confirm_str = a_web_element.get_dom_attribute('data-original-title')
        if confirm_str and 'Active' in a_web_element.text and confirm_str.startswith('Confirm'):
            # 已激活
            success = True
            active_flag = True
            write_last_active_date()
            print('NOIP activated, No action required')
            break
        elif a_web_element.text.startswith('Expires in '):
            # 需要进行激活操作
            button_web_elements = driver.find_elements(By.TAG_NAME, 'button')
            for button_web_element in button_web_elements:
                if 'Confirm' in button_web_element.text:
                    button_web_element.click()
                    sleep(60)
                    success = True
                    print('NoIp active success')
                    break
    return success, active_flag


def active_noip(mail, num):
    num = num + 1
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')  # 允许无沙盒模式运行
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    if os.name != 'nt':
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-dev-shm-usage')  # 在低内存系统上避免使用/dev/shm
    options.add_argument('window-size=900,900')

    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.implicitly_wait(60)
    actions = ActionChains(driver)
    login_state = True
    success = False
    active_flag = False
    try:
        login_num = 0
        while True:
            login(driver, mail, actions)
            login_num = login_num + 1
            if driver.current_url == login_success_url:
                print('login success')
                break
            if login_num < 50:
                print(f'Login failed, current URL：{driver.current_url}，logged in {login_num} times')
            else:
                print(f'Login failed, current URL：{driver.current_url}，logged in {login_num} times. This activation has failed!')
                login_state = False
                break

        if login_state:
            success, active_flag = active_dynamic_host(driver)
        # 页面跳转等待
        driver.implicitly_wait(60)
        sleep(30)
        if active_flag:
            # 激活状态，不需要重新激活
            print('Currently activated, no reactivation required.')
            return
        img_base64 = driver.get_screenshot_as_base64()
    except TimeoutError:
        if num < 4:
            active_noip(mail, num)
    except Exception as e:
        print(f'exception: {e}')
        img_base64 = driver.get_screenshot_as_base64()
    finally:
        driver.quit()

    message = MIMEMultipart("alternative")

    if success:
        write_last_active_date()
        message["Subject"] = "NOIP激活成功！！！！！！！"
    else:
        print('NoIp active fail')
        message["Subject"] = "NOIP激活失败，请及时处理！"

    message["From"] = email_username
    message["To"] = email_username
    message.attach(MIMEText(f'<h1>CURRENT_URL:{driver.current_url}</h1><br/><img src=\"data:image/jpg;base64,{img_base64}\"/>', "html"))
    with smtplib.SMTP_SSL(smtp_host, smtp_ssl_port) as server:
        # 登录到邮件服务器
        server.login(email_username, email_password)
        # 发送邮件
        server.sendmail(email_username, email_username, message.as_string())
    if not success and num < 4:
        sleep(600 * num)
        active_noip(mail, num)


def task():
    if is_need_run_task():
        mail = email_server()
        if mail is None:
            return
        check_email(mail)
        mail.logout()


if __name__ == '__main__':
    task()
