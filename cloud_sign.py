# -*- coding: utf8 -*-
import re
import requests
import asyncio
import json
import csv


user_info = {
	'username': '填写你的账号',
	'password': '填写你的密码',
	'学校id': '' # 学号登录才需要填写
}


csv_head = ['username', 'cookies']


class AutoSign(object):

	def __init__(self, username, password, schoolid=None):
		"""初始化就进行登录"""
		self.headers = {
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}
		self.session = requests.session()
		# 读取指定用户的cookies
		self.check_cookies_and_second_login(password, schoolid, username)
		# self.login(password, schoolid, username)
		self.save_cookies_to_csv(username)

	def save_cookies_to_csv(self, username):
		"""新cookies保存到csv文件中"""
		row = [username, self.session.cookies.get_dict()]
		with open('cookies.csv', 'a') as f:
			f_csv = csv.writer(f)
			# f_csv.writerow(csv_head)
			f_csv.writerow(row)

	def check_cookies_and_second_login(self, password, schoolid, username):
		"""检测csv文件内是否存有cookies,有则检测，无则登录"""
		with open('cookies.csv', 'r') as f:
			f_csv = csv.reader(f)
			for u in f_csv:
				# [username, cookies]
				if username == u[0]:
					# 设置cookies
					self.session.cookies.update(u[1])
					# 检测cookies是否有效
					r = self.session.get('http://i.mooc.chaoxing.com/settings/info?t=1584461245774')
					res = re.findall('<title>(.*)</title>', r.text)[0]
					if res == "用户登录":
						# 失效cookies
						self.login(password, schoolid, username)
			else:
				self.login(password, schoolid, username)
				self.save_cookies_to_csv(username)

	def login(self, password, schoolid, username):

		# 登录-手机邮箱登录
		if schoolid:
			r = self.session.post(
				'http://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(username, password, schoolid))
			return
		else:
			r = self.session.get(
				'https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid=&verify=0'.format(username, password),
				headers=self.headers)
			return
			# print(r.text)

	def _get_all_classid(self) -> list:
		"""获取课程主页中所有课程的classid和courseid"""
		re_rule = r'<li style="position:relative">[\s]*<input type="hidden" name="courseId" value="(.*)" />[\s].*<input type="hidden" name="classId" value="(.*)" />[\s].*[\s].*[\s].*[\s].*[\s].*[\s].*[\s].*[\s].*[s].*[\s]*[\s].*[\s].*[\s].*[\s].*[\s].*<a  href=\'.*\' target="_blank" title=".*">(.*)</a>'
		r = self.session.get(
			'http://mooc1-2.chaoxing.com/visit/interaction',
			headers=self.headers)
		res = re.findall(re_rule, r.text)
		return res

	async def _get_activeid(self, classid, courseid, classname):
		"""访问任务面板获取课程的活动id"""
		sign_re_rule = r'<div class="Mct" onclick="activeDetail\((.*),2,null\)">[\s].*[\s].*[\s].*[\s].*<dd class="green">.*</dd>'
		r = self.session.get(
			'https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId={}&jclassId={}'.format(
				courseid, classid), headers=self.headers, verify=False)
		res = re.findall(sign_re_rule, r.text)
		if res != []:  # 满足签到条件
			return {
				'classid': classid,
				'courseid': courseid,
				'activeid': res[0],
				'classname': classname}

	def general_sign(self, classid, courseid, activeid, checkcode=None):
		"""普通签到"""
		r = self.session.get(
			'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId={}&classId={}&fid=39037&courseId={}'.format(
				activeid, classid, courseid), headers=self.headers, verify=False)
		res = re.findall('<title>(.*)</title>', r.text)
		return res[0]

	def hand_sign(self, classid, courseid, activeid):
		"""手势签到"""
		hand_sign_url = "https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/signIn?\
		&courseId={}\
		&classId={}\
		&activeId={}".format(
			courseid, classid, activeid)
		r = self.session.get(hand_sign_url, headers=self.headers, verify=False)
		res = re.findall('<title>(.*)</title>', r.text)
		return res[0]

	def sign_in(self, classid, courseid, activeid):
		r = self.general_sign(classid, courseid, activeid)
		if "签到成功" in r:
			return r
		elif "手势签到" in r:
			sign_status = self.hand_sign(classid, courseid, activeid)
			return sign_status
		elif "位置签到" in r:
			pass

	def run(self):
		"""开始签到"""
		tasks = []
		# 获取所有课程的classid和course_id
		classid_courseId = self._get_all_classid()
		# 获取所有课程activeid
		for i in classid_courseId:
			coroutine = self._get_activeid(i[1], i[0], i[2])
			tasks.append(coroutine)

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		result = loop.run_until_complete(asyncio.gather(*tasks))
		for d in result:
			if d is not None:
				return '{}:{}'.format(d['classname'], self.sign_in(
					d['classid'], d['courseid'], d['activeid']))
		else:
			return "当前暂无签到任务"


def main_handler(event=None, context=None):
	if "username" and "password" in event.keys():
		# api请求
		s = AutoSign(event['username'], event['password'])
	else:
		# 自身函数执行的时候，才执行这个，可用于定时任务
		s = AutoSign(user_info['username'], user_info['password'])
	result = s.run()
	return result


# def main_handler():
# 	# 自身函数执行的时候，才执行这个，可用于定时任务
# 	s = AutoSign(user_info['username'], user_info['password'])
# 	result = s.run()
# 	return result


if __name__ == '__main__':
	main_handler()