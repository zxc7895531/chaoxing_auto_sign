![无图片描述][1]

这几天刷网课，每次老师喊签到的时候

都要登录->找到任务->签到

虽然操作也不是很麻烦，主要是刷课原本就要登录网站 ::aru:proud:: 

反正搞着好玩呗

## 接口使用
```
http://imgbed.z2blog.com/sign?username=登录用户名&password=密码
```
访问方式 GET
请求后，会自动签到所需要签到的课程
**接口仅做学习参考，不建议长期使用**

## 脚本使用
在脚本内，写入自己的账号密码，运行就可以自动签到了
可以将这个脚本放到flask框架，带着账号密码参数，请求一下就自动签到了

# 更新日志
课表classid获取
http://mooc1-1.chaoxing.com/api/workTestPendingNew

学号登陆url（post）
https://passport2.chaoxing.com/login?fid=39037

refer_0x001	http%3A%2F%2Fi.mooc.chaoxing.com
pid	-1
pidName	
fid	39037
fidName	武汉晴川学院
allowJoin	0
isCheckNumCode	1
f	0
productid	
t	true
uname	20170401036
password	OTk0LjIwMTd3dQ==
numcode	5703
verCode	

## 实现过程

###1、 登录
```
# 登录URL
# http://i.chaoxing.com/vlogin?passWord=passwordwu&userName=username
```
Post请求方式，参数就是账号密码

###2、 访问课程主页
```
# 课程主页url
# http://mooc1-2.chaoxing.com/visit/interaction
```
访问课程主页，是获取所有课程的classid和courseid，需要这两个参数，才能拼接出该门课程的签到url
![获取classid,courseid][2]

###3、访问任务页面
```
# 课程任务url
# https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId=209320132&jclassId=18855085
```
从课程主页获取classid courseid，现在就可以用到了，访问该课程任务url
这里的目的是为了获取`activeid`这个任务id
![无图片描述][3]

`onclick="activeDetail(129022258,2,null)"`
前面的数字就是`activeid` 后面的参数就是任务类型序号
```
2 签到
4 抢答
14 问卷
目前只知道这些
```
###4、签到

拿到所有参数后，就可以签到了，直接get请求一下即可
```
# 签到url
# https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId=126433134&classId=19047512&courseId=209403053
```

## 扩展
做好自动签到脚本后，可以和web结合
QQ机器人结合，真正实现方便的一键操作

  [1]: http://assets.z2blog.com/imgbed/2020/03/06/20200306880794.png
  [2]: http://assets.z2blog.com/imgbed/2020/03/06/20200306606197.png
  [3]: http://assets.z2blog.com/imgbed/2020/03/06/20200306740615.png
