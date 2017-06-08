import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

MUCHONG_USERNAME = ''  # write your username and password here
MUCHONG_PASSWORD = ''


class MuChong(object):

    def __init__(self, username, password):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
                        'Origin': 'http://muchong.com',
                        'Host': 'muchong.com'}
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = self.headers

    def login(self):
        resp = self.session.get('http://muchong.com/bbs/logging.php?action=login')
        my_formhash = re.search(r'name="formhash" value="(\w{8})"', resp.text).group(1)
        login_t = re.search(r't=(\d{10})', resp.text).group(1)
        login_url = 'http://muchong.com/bbs/logging.php?action=login&t='+login_t
        my_data = {'formhash': my_formhash,
                   'refer': '',
                   'username': self.username,
                   'password': self.password,
                   'cookietime': '31536000',
                   'loginsubmit': '提交'}
        login_result = self.session.post(login_url, data=my_data)
        verify_calc = re.search(u'问题：(\d+)(\D+)(\d+)等于多少?', login_result.text)
        number1 = int(verify_calc.group(1))
        number2 = int(verify_calc.group(3))
        if verify_calc.group(2) == '加':
            my_answer = number1 + number2
        elif verify_calc.group(2) == '减':
            my_answer = number1 - number2
        elif verify_calc.group(2) == '乘以':
            my_answer = number1 * number2
        else:
            my_answer = number1 / number2

        my_post_sec_hash = re.search(r'name="post_sec_hash" value="(\w+)"', login_result.text).group(1)
        my_new_data = {'formhash': my_formhash,
                       'post_sec_code': my_answer,
                       'post_sec_hash': my_post_sec_hash,
                       'username': self.username,
                       'loginsubmit': '提交'}

        self.session.post(login_url, data=my_new_data)

    def check_in(self):
        resp = self.session.get('http://muchong.com/bbs/memcp.php?action=getcredit')
        with open('./log.txt', 'a+') as f:
            try:
                if u'您现在的金币数' in resp.text:
                    print('今天已经登录！')
                    coins_number = BeautifulSoup(resp.text, 'html.parser').find('span', {'style': 'color:red;font-weight:bold;font-size:20px;'}).text
                    print('目前的金币数是：%s.' % coins_number)
                    f.write('当前时间为：%s. 今天已经登录，不用再重复登录了！\n' % datetime.now())
                elif u'您还没有登录' in resp.text:
                    print('登录异常，没有成功登录。')
                else:
                    credit_formhash = BeautifulSoup(resp.text, 'html.parser').find('input', {'name': 'formhash'})['value']
                    credit_data = {'formhash': credit_formhash,
                                   'getmode': '1',
                                   'message': '',
                                   'creditsubmit': '领取红包'}
                    r = self.session.post('http://muchong.com/bbs/memcp.php?action=getcredit', data=credit_data)
                    get_coins_number = BeautifulSoup(r.text, 'html.parser').find('span', {'style': 'color:red;font-weight:bold;font-size:30px;'}).text
                    coins = BeautifulSoup(r.text, 'html.parser').find('span', {'style': 'color:red;font-weight:bold;font-size:20px;'}).text
                    print('今天领取了金币数为：%s' % get_coins_number)
                    print('目前的总金币数为：%s' % coins)
                    f.write('本次登录成功，具体时间为：%s. 得到的金币数为：%s. 目前的总金币数为：%s.\n' % (datetime.now(), get_coins_number, coins))
            except Exception as e:
                print('签到失败', e)
                f.write('签到失败', e)

if __name__ == '__main__':
    my_muchong = MuChong(MUCHONG_USERNAME, MUCHONG_PASSWORD)
    my_muchong.login()
    my_muchong.check_in()
