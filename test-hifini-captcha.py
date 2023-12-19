# coding=utf-8
# 编程练习：滑块验证码
# python 3.8.18+selenium 4.15.2+ddddocr 1.4.10+Pillow 9.5.0

from selenium.webdriver.common.by import By
from selenium import webdriver
# 鼠标操作
from selenium.webdriver.common.action_chains import ActionChains
import time, random, re, base64
import ddddocr  # ddddocr识别验证框架
from datetime import datetime
import User_Password

# 将src数据转换成图片并保存在当前目录
def decode_image(src, name):
    """
    解码图片
    :param src: 图片编码
        eg:
            src="data:image/gif;base64,R0lGODlhMwAxAIAAAAAAAP///
                yH5BAAAAAAALAAAAAAzADEAAAK8jI+pBr0PowytzotTtbm/DTqQ6C3hGX
                ElcraA9jIr66ozVpM3nseUvYP1UEHF0FUUHkNJxhLZfEJNvol06tzwrgd
                LbXsFZYmSMPnHLB+zNJFbq15+SOf50+6rG7lKOjwV1ibGdhHYRVYVJ9Wn
                k2HWtLdIWMSH9lfyODZoZTb4xdnpxQSEF9oyOWIqp6gaI9pI1Qo7BijbF
                ZkoaAtEeiiLeKn72xM7vMZofJy8zJys2UxsCT3kO229LH1tXAAAOw=="

    :return: str 保存到本地的文件名
    """
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")

    # 2、base64解码
    img = base64.urlsafe_b64decode(data)

    # 3、二进制文件保存
    filename = "{}.{}".format(str(name), ext)
    with open(filename, "wb") as f:
        f.write(img)

    return filename
# 距离获取后，拖动验证码
def run_slidingblock(distance):
    tracks = get_tracks(distance)
    num = 0 
    for i in tracks:
        num += i
    if distance - 2 < num and num < distance + 2:
        track = tracks
    else:
        a = distance - num
        tracks.append(a)
        track = tracks
    drag = driver.find_element(by=By.CLASS_NAME, value='verify-move-block')
    ActionChains(driver).click_and_hold(drag).perform()
    for x in track:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    ActionChains(driver).release().perform()
# 获取距离集合，模拟人拖动
def get_tracks(distance, rate=0.6, t=0.2, v=0):
	"""
	将distance分割成小段的距离
	:param distance: 总距离
	:param rate: 加速减速的临界比例
	:param a1: 加速度
	:param a2: 减速度
	:param t: 单位时间
	:param t: 初始速度
	:return: 小段的距离集合
	"""
	tracks = []
	# 加速减速的临界值
	mid = rate * distance
	# 当前位移
	s = 0
	# 循环
	while s < distance:
		# 初始速度
		v0 = v
		if s < mid:
			a = 40
		else:
			a = -3
		# 计算当前t时间段走的距离
		s0 = v0 * t + 0.5 * a * t * t
		# 计算当前速度
		v = v0 + a * t
		# 四舍五入距离，因为像素没有小数
		tracks.append(round(s0))
		# 计算当前距离
		s += s0
	return tracks
#计算背景图片中空缺区域到左侧端点的距离

if __name__ == '__main__':

    driver = webdriver.Firefox()
    driver.get("https://hifini.com/user-login.htm")
    driver.maximize_window()
    # 输入用户名和密码
    driver.find_element(By.ID, 'email').send_keys(User_Password.UserName)
    driver.find_element(By.ID, 'password').send_keys(User_Password.PassWord)
    # 点击人机验证按钮
    driver.find_element(By.ID, 'captcha').click()
    driver.implicitly_wait(10)

    # 人机验证成功标志,进行人机验证直到验证成功
    success_flag = True
    while success_flag:
        # 获取人机验证的带缺口的背景图和缺口目标图块
        time.sleep(2)
        background_src = driver.find_element(By.CLASS_NAME, 'backImg').get_attribute('src')
        target_src = driver.find_element(By.CLASS_NAME, 'bock-backImg').get_attribute('src')
        # print(background, target)
        decode_image(background_src, 'background')
        decode_image(target_src, 'target')
        # ddddocr实例化，获取背景中缺口的左上右下四个参数
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        with open('target.png', 'rb') as f:
            target_bytes = f.read()
        with open('background.png', 'rb') as f:
            background_bytes = f.read()
        res = det.slide_match(target_bytes, background_bytes, simple_target=True)  # 简单图片带参数simple_target
        # print(res)
        distance = res['target'][0]
        # print(distance)
        # 输入滑块移动距离参数，实现模拟拖动滑块拼图验证
        run_slidingblock(distance)
        time.sleep(3)
        captcha_text = driver.find_element(By.ID, 'captcha').text
        # print(captcha_text)
        if captcha_text == '验证成功':
            success_flag = False
            break

    # 点击登录按钮
    driver.find_element(By.ID, 'submit').click()
    driver.implicitly_wait(10)
    # 找到签到标签并进行签到操作
    sg_sign = driver.find_element(By.ID, 'sg_sign')
    """
    time_now = time.strftime("%H:%M:%S",time.localtime())
    sg_sign.click()

    """
    while True:
        time_now = time.strftime("%H:%M:%S", time.localtime())
        if time_now == "00:00:00":
            sg_sign.click() # 对签到标签进行点击操作
            #人机验证，拖动滑块移动实现
            move_block = driver.find_element(By.CLASS_NAME, 'verify-move-block')
            bar_area = driver.find_element(By.CLASS_NAME, 'verify-bar-area')
            move_distance = bar_area.size['width'] - move_block.size['width']
            run_slidingblock(move_distance)
            break # 退出循环

    time.sleep(1)
    driver.save_screenshot(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+'.png') # 屏幕截图保存       
    driver.get('https://sctapi.ftqq.com/SCT130527TxL3yQVPGSag7mZ8b6XJ68Kz2.send?title=Hifini_web_Sign&desp='+'Localtime  恭喜您在 '+datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f ")+'和 '+time_now+' 时刻对 '+driver.title+' 进行了签到!!! \n')  
    driver.get('https://hifini.com/my.htm')
    driver.save_screenshot(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+'.png') # 屏幕截图保存    

    driver.quit()  # 关闭Firefofox Broswer 并释放内存资源