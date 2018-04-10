#!/usr/bin/python
# -*- coding: UTF-8 -*-

#设置编码格式为utf-8，为了可以打印出中文字符
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#导入urllib2模块，用于通过url获取网页内容
#import urllib2

#导入BeautifulSoup模块，用于解析网页的内容
from bs4 import BeautifulSoup

#导入webdriver,提供一个涉及良好的面相对象的API
from selenium import webdriver

#导入python操作excel模块
import xlwt


#通过url得到页面全部内容
def get_url_content(url):

	#这里由于需要爬取的内容在iframe里，直接通过一般的urllib2获取不到
	#而selenium的webdriver可以获取到iframe里面的内容

	#这里使用的chrome driver
	#将解压的chromedriver文件放到chrome安装文件夹里，然后将这个路径添加到系统的环境变量里
	browser = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver') #括号里是chromedriver所在的目录
	browser.get(url)
	iframe = browser.find_element_by_tag_name("iframe")
	browser.switch_to.default_content()
	browser.switch_to.frame(iframe)
	iframe_source = browser.page_source
	return iframe_source
	

	#构造发送请求
	#request = urllib2.Request(url)

	#发出请求并取得响应
	#response = urllib2.urlopen(request)

	#获取页面内容
	#html = requests.get(url).text

	#返回网页内容
	#return html

#通过xlwt设置utf编码格式，并返回一个excel对象‘book'
book = xlwt.Workbook(encoding='utf-8', style_compression=0)

#通过这个book对象创建一个sheet，命名为“云音乐飙升榜”
sheet = book.add_sheet('云音乐每日飙升榜', cell_overwrite_ok = True)
#给这个sheet添加4列名称
sheet.write(0,0,'歌曲名称')
sheet.write(0,1,'歌曲时长')
sheet.write(0,2,'歌曲歌手')
sheet.write(0,3,'歌曲详情url')

#定义一个全局的行数n，为了下面parser_to_excel方法写入excel时可以找到从哪一行开始写入
n=1

#通过BeautifulSoup解析后的结构来获取内容，并存入excel
#注意，因为不同的网页结构不同，爬取其他网页时，只需要改动这里的内容就可以了，其他东西不用改（main方法里的某些地方还是要改动，但主题思想不变）
#存入excel也是这里的特定操作，当然也可以选择存入数据库或者缓存

def parser_to_excel(soup):
	#查看网页可以看到我们要获取的信息都在class='j-flag'里面，所以获取到它，再获取到<tbody>里面的<td>,组成一个list
	content_list = soup.find('tbody').find_all('tr')


	#print content_list  用来查看获取的内容是否正确
	#循环tr标签列表
	for song_item in content_list:
		#获取每个<tr>里面的<td>
		item_list = song_item.find_all('td')
		#print item_list
		#通过查看网页，可以看见一首歌也就是一个<tr>里面包含四个<td>

		#第二个<td>里面的a标签是歌曲链接，b标签是歌曲名称
		#拼接url。http://music.163.com/#/song?id=550138047
		song_detail_url = 'http://music.163.com/#'+item_list[1].find_all('a')[0].get('href')
		song_name = item_list[1].find_all('b')[0].get('title')
		
		#第三个<td>里面class="u-dur"标签可以获取歌曲时长
		song_dur = item_list[2].find(class_='u-dur').text

		#第四个<td>里面的span标签的title可以获取歌曲的歌手名称
		song_singer = item_list[3].find('span').get('title')

		#打印爬到的信息
		print("song name: "+str(song_name)+", song's duration: "+str(song_dur)+", song's singer: "+str(song_singer)+", song's url: "+str(song_detail_url))

		#把信息存入excel
		#sheet就是前面已经初始化好的全局sheet
		#逐个写入sheet。前两个数字代表行列(1,0,name)就是在第二行第一列写入name
		#这里的行我们取方法外面的n，代表当前从第n行开始写
		#但这里这个n必须定义为全局变量，不然会报错
		global n
		sheet.write(n,0,song_name)
		sheet.write(n,1,song_dur)
		sheet.write(n,2,song_singer)
		sheet.write(n,3,song_detail_url)

		#每次存入后把n加一。代表下一次从下一行开始写
		print("pushing data to "+str(n)+" row \n")
		n = n+1


#程序从这里运行
if __name__=="__main__":

	#设置爬取的初始url
	base_url = 'http://music.163.com/#/discover/toplist?id=19723756'

	#获取初始化页面内容
	content = get_url_content(base_url)

	#把内容解析成BeautifulSoup结构
	soup = BeautifulSoup(content, 'html5lib')

	#获取当前页的信息并存入excel
	parser_to_excel(soup)

	book.save(u'云音乐每日飙升榜.xls')#保存