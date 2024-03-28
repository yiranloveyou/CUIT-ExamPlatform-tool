
# ┌───────────────────────────────────────────────────────┐
# │                                                       │
# │                       README                          │
# │                                                       │
# │ 1. 在使用前请确保已安装所需的库和配置浏览器webdriver。    │
# │ 2. 确保提供的账号和密码是有效的。                        │
# │ 3. 确保你连接的是校园网。                               │
# │ 4. 将"课程名称"替换为您想要爬取的实际课程名称。           │
# │ 5. 题型选择请对应序号，更多说明请参看参数一栏。           │
# │ 6. 运行后输出文件将保存在与Python文件相同的目录中。       │
# │ 7. 该脚本目前实现了大部分功能，但仍有许多问题，同时由于    │ 
# │    网站可能发生变化，本脚本随时可能失效                  │ 
# │                                                       │ 
# │               声明：此脚本仅用作学习使用                │ 
# │                                                       │                                                      
# └───────────────────────────────────────────────────────┘

#############################################################
#-----------------------requirement-------------------------#
"""
pip install selenium
pip install request
pip install lxml

Chrome浏览器webdriver下载，请自行百度
"""
#############################################################

#导入库
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions
import time
import requests
from lxml import etree


############################################################################################
#------------------------------------------参数调整-----------------------------------------#

#账号密码
username = "2022122146"
password = "2022122146"

#课程名称
course_name='"C语言程序设计"'

#题目类型
question_type='1000204'

#类型对照表（后面有*号的表示目前支持题目类型）
# 100020101 选择题 *
# 1000203 判断题 *
# 1000204 填空题
# 1000206 编程题 *
# 1000207 综合题 *
# 1000208 改错题 

#填空和改错题与其他题型不同，其他题型答案可以从源码中获取
#但是这两个题的答案是通过动态加载得来的
#这两个题目类型功能还不完善，但可以试一试能不能用

#sleep时间
i=0.1

#-------------------------------------------------------------------------------------------#
#############################################################################################

# 使用Chrome浏览器，需提前安装Chrome浏览器并配置对应的webdriver
option=Options()

option.add_argument('--headless') #无头浏览器，不显示界面
option.add_argument('--disable-gpu')  # 禁用GPU加速，避免某些问题
option.add_argument('--no-sandbox')  # 避免在Linux环境下的一些限制

driver = webdriver.Chrome(options=option)

#url
url = r"http://exam.cuit.edu.cn/index.php?r=front%2Ftest%2Findex"
url1=r"http://exam.cuit.edu.cn/index.php?r=front%2Fsite%2Flogin"

#请求头构造
headers={
     "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76"
    }

data={
    "r":"front/site/login",
    "StuNumber":username,
    "password":password
}

#维持登录状态
session=requests.Session()
response=session.post(url=url1,data=data,headers=headers)
print("连接状态："+str(response.status_code))


#到达目标网页
def start():
    # 访问登录页面
    driver.get(url)

    # 输入用户名和密码
    username_input = driver.find_element(By.NAME, "StuNumber")  # 使用By.NAME作为定位方式
    password_input = driver.find_element(By.NAME, "password") 
    username_input.send_keys(username)
    password_input.send_keys(password)

    # 提交登录表单
    password_input.send_keys(Keys.ENTER)

    #模拟点击
    time.sleep(i)
    si_button=driver.find_element(By.XPATH,'//button[@class="navbar-expand-toggle"]')
    si_button.click()
    time.sleep(i)
    si_button=driver.find_element(By.LINK_TEXT,'进入练习')
    si_button.click()
    time.sleep(i)


#获取所有链接
def get_link():
    #切换到iframe
    frame1 = driver.find_element(By.XPATH, '//iframe[@onload="reinitIframe1();"]')
    driver.switch_to.frame(frame1)
    li_list = driver.find_elements(By.XPATH, '//li[@class="slide"][@id='+course_name+']//li[@class="sstop"]//a')#定位要爬取的课程
    #切出iframe
    driver.switch_to.default_content() 
    #循环获取目标网页链接
    for li in li_list:
        time.sleep(i)
        driver.switch_to.frame(frame1)
        href = li.get_attribute('href')
        text = li.get_attribute('text') 
        driver.switch_to.default_content()
        #判断题目类型
        if question_type != '1000204' and question_type != '1000208':
            get_info1(href,text)
        elif question_type == '1000204':
            get_info2(href,text)
        elif question_type == '1000208':
            get_info3(href,text)



#获取页面_1:静态页面
def get_info1(href,text):
    fp.write(text+"\n")
    page_text=session.get(url=href,headers=headers).text
    tree=etree.HTML(page_text)
    #获取内容
    blanks=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//text()[not(ancestor::div[@style="float:left;"])]')#过滤掉无用信息
    i=0
    for i in range(len(blanks)-1):
        fp.write(blanks[i].strip())  # 使用strip()方法去除多余的空白字符和换行符
        fp.write('\n')  # 写入换行符，使每条信息单独一行


#获取页面_2：动态加载数据（填空题）
def get_info2(href,text):
    fp.write(text+"\n")
    page_text=session.get(url=href,headers=headers).text
    tree=etree.HTML(page_text)
    #获取题目
    #blanks=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//text()')
    blanks=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//button[@name="1"]//div[@class="noFlow"]//text()')
    answers=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//input[@class="answ TKanswer"]//@name')
    
    if not blanks:
        print("No blanks found for this iteration.")
    else: 
        #对动态请求地址发送post请求
        url2=r"http://exam.cuit.edu.cn/index.php?r=front%2Ftest%2Fget-fill-answer"
        i=0
        for i in range(len(blanks)-1):
            data2={
                "r":"front/test/get-fill-answer",
                "QuestionBh":answers[i]
            }
            response=session.post(url=url2,data=data2,headers=headers)
            answer=response.text
            #这里发现结果返回的json字符串，解码
            decoded_answer = answer.encode().decode('unicode_escape')
            print("1")
            fp.write(blanks[i].strip())
            fp.write(decoded_answer)
            fp.write("\n")

#获取页面_3：动态加载数据（改错题）
def get_info3(href,text):
    fp.write(text+"\n")
    page_text=session.get(url=href,headers=headers).text
    tree=etree.HTML(page_text)
    #获取题目
    blanks1=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//text()[not(ancestor::div[@style="float:left;"])]')#过滤掉无用信息
    blanks=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//button[@name="1"]//div[@class="noFlow"]//text()')
    answers=tree.xpath('//div[@class="row '+question_type+'"][@id="'+question_type+'"]//input[@class="answ JDanswer"]//@name')
    if not blanks:
        print("No blanks found for this iteration.")
    else: 
        #对动态请求地址发送post请求
        url3=r"http://exam.cuit.edu.cn/index.php?r=front%2Ftest%2Fget-correct-answer"
        i=0
        for i in range(len(blanks)-1):
            data3={
                "r":"front/test/get-correct-answer",
                "QuestionBh":answers[i]
            }
            response=session.post(url=url3,data=data3,headers=headers)
            answer=response.text
            print("1")
            fp.write(blanks1[i])
            fp.write("\n")
            fp.write(answer)
            fp.write("\n")

#总程序
if __name__=="__main__":
    print("开始爬取！")
    start_time=time.time()
    start()
    with open("./题库.txt", "w", encoding="utf-8") as fp:
        get_link()
    # 关闭浏览器
    driver.quit()
    end_time=time.time()
    dur=end_time-start_time
    print("运行完成!")
    print("运行时间"+str(round(dur,2))+"s")
