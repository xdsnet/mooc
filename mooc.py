# !/usr/bin/env python
# coding=utf-8


import requests
import re
import os
import urllib
import sys

pdfNum = 0  # PDF 文件数量
progress = 0  # 正在处理第progress个
pageTitle = ''


# 请求PDF地址
# 比较慢
def getPdfUrl(params=''):
    global progress
    global pdfNum
    progress += 1
    print("正在处理第: %d/%d 个pdf" % (progress, pdfNum))

    url = 'http://www.feemic.cn/api/mooc/get_pdf'
    # 参数处理
    params = params[21:-1]
    params = re.sub(":", "':'", params)
    params = re.sub(",", "','", params)
    params = re.sub("{", "{'", params)
    params = re.sub("}", "'}", params)
    try:
        resp = requests.post(url=url, data=eval(params))
    except:
        print("获取pdf链接错误")
        return -1
    # print(resp.url)
    return resp.url


# print(getPdfUrl("'/api/mooc/get_pdf', {cid:879014,unitId:1003544522}"))

# 提取PDF文件标题
def getPdfTitle(title):
    # '>期末考试复习题答案</a><span class="c-label c-label--warning">PDF'
    ans = title[1:-46] + ".pdf"
    # 去掉不允许的文件名  \/:*?"<>|
    p = re.compile(r'\\|/|:|\*|\?|"|<|>|\|')
    ans = p.sub("-", ans)
    return ans


# 提取视频标题
def getMp4Title(title):
    # .mp4 target="_blank" rel="noreferrer">图像合成例子</a>
    ans = title[38:-4] + ".mp4"
    # 去掉不允许的文件名  \/:*?"<>|
    p = re.compile(r'\\|/|:|\*|\?|"|<|>|\|')
    ans = p.sub("-", ans)
    return ans


# 提取富文本链接
def getRtextUrl(url):
    ans = "[InternetShortcut]\nURL="
    ans = ans + "http://www.feemic.cn" + url
    return ans


# 提取富文本标题
def getRtextTitle(title):
    # >在Windows上安装C语言编程软件</a><span class="c-label c-label--red">RText</span>
    ans = title[1:-51] + '.url'
    # 去掉不允许的文件名  \/:*?"<>|
    p = re.compile(r'\\|/|:|\*|\?|"|<|>|\|')
    ans = p.sub("-", ans)
    return ans


# 重命名
def ren(a, b):
    s = a.split('/')[-1]
    return "& ren " + s + " \"" + b+"\""


def reName(url, title):
    l = list(map(ren, url, title))
    l = ' '.join(l)
    return "chcp 65001 &"+l
    # print(l)

# 解码pdf
def unquote(url):
    ans = urllib.parse.unquote(url)
    return ans.split('=')[-1]
    

# 写入文件

# 将列表con分行写入name中
def write(con, name):
    # print(str(con))
    f = open(pageTitle + "\\" + name, 'w', encoding='gbk')
    f.write('\n'.join(con))
    f.close()


# 写入字符串
def writeStr(str, name):
    f = open(pageTitle + "\\" + name, 'w', encoding='gbk')
    f.write(str)
    f.close()


# 如果不存在,则创建目录
def mkdir():
    if not os.path.exists(pageTitle):
        os.mkdir(pageTitle)


def getAll(url):
    resp = requests.get(url).text
    global pageTitle
    pagePattern = re.compile(r'<p><b>.+</b></p>')
    pageTitle = re.findall(pattern=pagePattern, string=resp)[0][6:-8]
    print(pageTitle)
    mkdir()

    # 视频正则
    mp4UrlPattern = re.compile(r'http://v\.stu\.126\.net.+\.mp4')
    mp4Url = re.findall(pattern=mp4UrlPattern, string=resp)
    write(mp4Url, "Mp4url.txt")

    # 视频的题目
    mp4TitlePattern = re.compile(r'\.mp4 target="_blank" rel="noreferrer">.+</a>')
    mp4Title = re.findall(pattern=mp4TitlePattern, string=resp)
    mp4Title = list(map(getMp4Title, mp4Title))
    for i in range(mp4Title.__len__()):
        mp4Title[i] = str(i+1) + mp4Title[i]

    # 视频重命名
    ans = reName(mp4Url, mp4Title)
    writeStr(ans, "mp4重命名.cmd")
   

    # PDF正则
    pdfUrlPattern = re.compile(r"\('/api/mooc/get_pdf', {cid:\d+,unitId:\d+}\)")
    pdfUrl = re.findall(pattern=pdfUrlPattern, string=resp)
    global pdfNum
    pdfNum = pdfUrl.__len__()
    pdfUrl = list(map(getPdfUrl, pdfUrl))

    # print(pdfUrl)
    write(pdfUrl, "PDF.txt")

    # PDF题目
    pdfTitlePattern = re.compile(r'>.+</a><span class="c-label c-label--warning">PDF')
    pdfTitle = re.findall(pattern=pdfTitlePattern, string=resp)
    pdfTitle = list(map(getPdfTitle, pdfTitle))
    # PDF 重命名
    decodePdfUrl = map(unquote, pdfUrl)
    for i in range(pdfTitle.__len__()):
        pdfTitle[i] = str(i+1) + pdfTitle[i]

    ans = reName(decodePdfUrl, pdfTitle)
    writeStr(ans, "PDF重命名.cmd")
    # print(pdfTitle)


    # 富文本
    rtextUrlPattern = re.compile(r"/mooc_rtext/\d+")
    rtextUrl = re.findall(pattern=rtextUrlPattern, string=resp)
    rtextUrl = list(map(getRtextUrl, rtextUrl))

    # print(rtextUrl)

    rtextTitlePattern = re.compile(r'>.+</a><span class="c-label c-label--red">RText</span>')
    rtextTitle = re.findall(pattern=rtextTitlePattern, string=resp)
    rtextTitle = list(map(getRtextTitle, rtextTitle))
    # print(rtextTitle)
    # 创建指向网址的快捷方式
    # 不知道为什么用map不起作用
    for i in range(rtextTitle.__len__()):
        writeStr(rtextUrl[i], rtextTitle[i])



if __name__ == '__main__':
    # 课程地址
    url = 'http://www.feemic.cn/mooc_search/1002321008'
    # if sys.argv.__len__() == 1:  # 未输入课程地址
    #     print("请输入课程url")
    #     os._exit(0)
    # url = sys.argv[1]
    getAll(url)
