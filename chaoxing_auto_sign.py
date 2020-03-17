import re
import requests
import asyncio
import json


class AutoSign(object):

	def __init__(self, username, password, schoolid=None):
		"""初始化就进行登录"""
		self.headers = {
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}
		self.session = requests.session()
		# 登录-手机邮箱登录
		if schoolid:
			r = self.session.post(
				'http://passport2.chaoxing.com/api/login?name={}\
				&pwd={}\
				&schoolid=\
				{}&verify=0'.format(username, password,schoolid))
		else:
			r = self.session.post(
				'http://i.chaoxing.com/vlogin?\
				passWord={}\
				&userName={}'.format(password, username), headers=self.headers)

		print(r.text)

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

		# if checkcode is not None:
		# 	'''手势签到'''
		# 	# 手势签到验证URL
		# 	# https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/checkSignCode?activeId=134706366&signCode=147896325
		# 	check_status = self.session.get(
		# 		'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/checkSignCode?activeId={}&signCode={}'.format(
		# 			activeid, checkcode), headers=self.headers, verify=False)
		# 	check_status = json.loads(check_status.text)
		# 	if check_status['result'] == '0':
		# 		return '验证码错误'
		# 	r = self.session.get(
		# 		'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/signIn?courseId={}&classId={}&activeId={}'.format(
		# 			courseid, classid, activeid), headers=self.headers, verify=False)
		# 	res = re.findall('<title>(.*)</title>', r.text)
		# 	return res[0]
		#
		# else:
		r = self.session.get(
			'https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?\
			activeId={}\
			&classId={}\
			&fid=39037\
			&courseId={}'.format(
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
		classid_courseId = self._get_all_classid()
		tasks = []
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


if __name__ == '__main__':
	s = AutoSign('此处填写你的账号', '此处填写你的密码')
	print(s.run())
