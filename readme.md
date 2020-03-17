## 功能描述
只管登录，签到交给程序就好了

创建Autosign对象（参数是账号和密码，支持学号登录）

支持普通签到和手势签到

这个脚本只实现了签到功能

并不具备，24小时挂机自动签到的功能

### 学号登录需手动获取schoolid
关于学号登录方式，有一个额外参数`schoolid`

http://passport2.chaoxing.com/login

![schoolid][5]


## 更新日志
3.17 更新手势签到，无需手动输入验证码

3.15 支持学号方式登录,目前可以通过(手机号码，邮箱，学号登录)

3.10 新增手势签到(具体使用在下方)

## 其他签到脚本推荐
我们学校目前只有手势签到和普通签到，涉及不到全部
所以推荐些其他的项目
| 项目地址                                                | 开发语言   | 备注                                           |
| ------------------------------------------------------- | ---------- | ---------------------------------------------- |
| https://github.com/Wzb3422/auto-sign-chaoxing           | TypeScript | 超星学习通自动签到，梦中刷网课       |
| https://github.com/Huangyan0804/AutoCheckin             | Python     | 学习通自动签到，支持手势，二维码，位置，拍照等 |
| https://github.com/aihuahua-522/chaoxing-testforAndroid | Java       | 学习通（超星）自动签到               |
| https://github.com/yuban10703/chaoxingsign              | Python     | 超星学习通自动签到                   |


## 接口使用(非长期有效)
```
http://imgbed.z2blog.com/sign?username=登录用户名&password=密码
```
请求方式GET
| 参数     |    说明    | 是否必须 |
| :------- | :--------: | :------: |
| username |  手机号码  |    是    |
| password |    密码    |    是    |


请求后，会自动签到所需要签到的课程
**接口仅做学习参考，不建议长期使用**


## 脚本使用
在脚本内，写入自己的账号密码，运行就可以自动签到了
可以将这个脚本放到flask框架，带着账号密码参数，请求一下就自动签到了


## 实现过程

### 1、 登录
```
# 手机号码及邮箱登录URL
# http://i.chaoxing.com/vlogin?passWord=passwordwu&userName=username

# 学号登录URL
# http://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0
```
Post请求方式，参数就是账号密码
关于学号登录方式，有一个额外参数`schoolid`

http://passport2.chaoxing.com/login

![schoolid][5]


### 2、 访问课程主页
```
# 课程主页url
# http://mooc1-2.chaoxing.com/visit/interaction
```
访问课程主页，是获取所有课程的classid和courseid，需要这两个参数，才能拼接出该门课程的签到url
![获取classid,courseid][3]

### 3、访问任务页面
```
# 课程任务url
# https://mobilelearn.chaoxing.com/widget/pcpick/stu/index?courseId=209320132&jclassId=18855085
```
从课程主页获取classid courseid，现在就可以用到了，访问该课程任务url
这里的目的是为了获取`activeid`这个任务id
![无图片描述][4]

`onclick="activeDetail(129022258,2,null)"`
前面的数字就是`activeid` 后面的参数就是任务类型序号
```
2 签到
4 抢答
14 问卷
目前只知道这些
```
### 4、签到

拿到所有参数后，就可以签到了，直接get请求一下即可
```
# 签到url
# https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId=126433134&classId=19047512&courseId=209403053
```

## 扩展
做好自动签到脚本后，可以和web结合
QQ机器人结合，真正实现方便的一键操作


  [1]: http://assets.z2blog.com/imgbed/2020/03/06/20200306880794.png
  [2]: https://www.z2blog.com//usr/uploads/2020/03/493803449.png
  [3]: http://assets.z2blog.com/imgbed/2020/03/06/20200306606197.png
  [4]: http://assets.z2blog.com/imgbed/2020/03/06/20200306740615.png
  [5]: https://ae01.alicdn.com/kf/U99b1d82401c14c2192b3ec5e81fbaa05F.png


