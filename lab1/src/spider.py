'''
Project: webLab01_spider
Author: Eric_LiCH
LastEditors: Eric_LiCH
E-mail: Eric_LiCH@outlook.com
Date: 2022-09-19 22:04:50
LastEditTime: 2022-10-07 22:02:47
'''
import json
import os
import requests
import bs4
import time

#api_key = 'apikey=0b2bdeda43b5688921839c8ecb20399b' #0b2bdeda43b5688921839c8ecb20399b
default_headers_with_cookie = {
    "Cookie" : 'bid=lNKvpX0Q5Zk; ll="118183"; __gads=ID=8440acce0f3ad93e-22cbbf98a9d60007:T=1663641138:RT=1663641138:S=ALNI_MYHyZ6RE0L4ryUh__Io30smMYxZ3Q; gr_user_id=3b7b0844-411f-46c6-88bb-43c9b4a5cd69; ct=y; viewed="1858513_2297697_2230208_1051231_4123116_26304258_2025999_35985166"; __utmz=30149280.1665224369.6.3.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; dbcl2="263482026:N+djeMlo9i0"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.26348; __yadk_uid=AuJ3QFX8dbuYgMtaRUcDsubN9LqlluoJ; ck=syEJ; _pk_ref.100001.8cb4=["","",1665660296,"https://cn.bing.com/"]; _pk_id.100001.8cb4=b51467a29f112d6d.1663641127.3.1665660296.1665226050.; _pk_ses.100001.8cb4=*; ap_v=0,6.0; __gpi=UID=000009d0f48594b8:T=1663641138:RT=1665660298:S=ALNI_MZTROuksvlQkDHv52z-fLTJUHH3_g; __utma=30149280.1984371564.1663641127.1665224369.1665660298.7; __utmc=30149280; __utmt=1; __utmb=30149280.2.10.1665660298',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
douban_book_header = 'https://book.douban.com/'
douban_movie_header = 'https://movie.douban.com/'
default_headers = {}


'''
description: using the request.get() to get the target url
param {str} url
param {bool} with_cookie
return {class response}
'''
def open_url(url, with_cookie = False):
    #fetch_proxy(500)
    #proxys = proxypool()
    if with_cookie:
        res = requests.get(url, headers = default_headers_with_cookie )
    else:
        res = requests.get(url, headers = default_headers )#proxies = random.choice(proxys)
    return res



def book_crawl():
    #TODO  get the book info
    book_list = []
    all_dic = []
    book_json = json.loads(json.dumps({}))

    with open('Book_id.txt','r') as book_id:
        for line in book_id.readlines():
            book_list.append(line.strip())
    for book_id in book_list:
        tag_list = []
        content_list = []

        start_time = time.time()
        url = douban_book_header + 'subject/' + book_id +'/'

        response = open_url(url,True)
        if response.status_code >= 400:
            continue

        try:
            try:
                print('尝试直接抓取中...')
                soup = bs4.BeautifulSoup(response.text,"html.parser")
                book_title = str(soup.find('span',property = 'v:itemreviewed').text).strip()
            except:
                print(r'直接抓取失败/(ㄒoㄒ)/~~'+'\n'+'开始尝试使用cookie抓取...')
                new_response = open_url(url, with_cookie= True)
                soup = bs4.BeautifulSoup(new_response.text,"html.parser")
                book_title = str(soup.find('span',property = 'v:itemreviewed').text).strip()
            
            print('成功抓取电影{}'.format(book_title))
            tag_list.append('书名')
            print('{}: start: {}'.format(book_title,str(start_time)),end='')
            content_list.append(book_title)

            book_score = soup.find('strong', property="v:average")
            tag_list.append('评分')
            content_list.append(str(book_score.next).strip())

            book_short_info = soup.find('div',id = 'info')
            book_span = book_short_info.find_all('span',{'class':'pl'})
            
            for each in book_span:
                each_str = str(each.text).strip().replace(':','')
                try:
                    if each.find_next_sibling().attrs['href'] != None:
                        each_content = str(each.find_next_sibling().text).strip().replace(' ','').replace('\n',' ')
                except:
                    each_content = str(each.next_sibling.text).strip().replace(' ','').replace('\n',' ')
                tag_list.append(each_str)
                content_list.append(each_content)

            book_intro = soup.find('div',{'class':'related_info'})

            h2_list = book_intro.find_all('h2')
            tag_list.append(h2_list[0].span.text)
            tag_list.append(h2_list[1].span.text)

            intro_content_list = book_intro.find_all('div',{'class':'intro'})
            try :
                content_list.append(intro_content_list[-2].p.text)
            except:
                content_list.append(intro_content_list[0].p.text)
            content_list.append(intro_content_list[-1].p.text)

            book_dic = dict(zip(tag_list,content_list))
            all_dic.append(book_dic)
            
            use_time = time.time() - start_time
            print('\tusetime {}s'.format(str(use_time)))
            #break
        except:
            print('抓取书号为{}的图书失败，默认跳过'.format(str(book_id)))
            continue

        time.sleep(3)

    with open('book.json','w',encoding='utf-8') as fp:
        book_json['书籍'] = all_dic
        json.dump(book_json,fp,ensure_ascii=False)

'''    with open("{}.csv".format('book'), 'a+', newline='', encoding='utf-8') as book_csv:
        writer = csv.writer(book_csv)
        writer.writerow(['书名', '评分','作者', '出版社', '出版年', 'ISBN', '内容简介','作者简介'])
        writer.writerows(book_info_list)'''

def movie_crawl():
    movie_json = json.loads(json.dumps({}))
    movie_list = []
    all_dic = []
    with open('Movie_id.txt','r') as movie_id:
        for line in movie_id.readlines():
            movie_list.append(line.strip())
    for movie_id in movie_list:
        tag_list = []
        content_list = []
        url = douban_book_header + 'subject/' + movie_id +'/'

    #TODO : 爬取基本信息
        response = open_url(url,True)
        if response.status_code >= 400:
            continue

        soup = bs4.BeautifulSoup(response.text,"html.parser")

        try:
            start_time = time.time()

            movie_title = str(soup.find('span',property = "v:itemreviewed").text).strip()
            print('{} start!'.format(movie_title))
            tag_list.append('电影名')
            content_list.append(movie_title)

            movie_score = soup.find('strong', property="v:average")
            tag_list.append('评分')
            content_list.append(str(movie_score.next).strip())

            movie_short_info = soup.find('div',id = 'info')
            movie_span = movie_short_info.find_all('span',{'class':'pl'})
            
            for each in movie_span:
                each_str = str(each.text).strip().replace(':','')
                try:
                    if each.find_next_sibling().a.attrs['href'] != None:
                        each_content = []
                        members = each.parent.find_all('a')
                        for member in members:
                            each_content.append(member.text)
                        content_list.append(each_content)
                except:
                    if each_str == '类型':
                        movie_type = each.find_all('span',roperty="v:genre")
                        whole_type = ''
                        for each_type in movie_type:
                            str_type = str(each_type).strip()
                            whole_type += (str_type + '/')
                        whole_type.strip('/')
                        each_content = whole_type
                    else:        
                        each_content = str(each.next_sibling.text).strip().replace(' ','').replace('\n',' ')
                    content_list.append(each_content)
                tag_list.append(each_str)

            movie_intro = soup.find('div',{'class':'related-info'})

        #TODO : 爬取剧情简介
            tag_list.append('剧情简介')
            try:
                intro_content = movie_intro.find('div',{'class':'all hidden'})
                content_list.append(intro_content)
            except:
                intro_content = movie_intro.find('span' , property="v:summary")
                content_list.append(intro_content)
            
        #TODO : 爬取演职员表网页
            tag_list.append('演职员表')
            staff_url = url + '/celebraties'
            staff_res = open_url(staff_url)
            staff_soup = bs4.BeautifulSoup(staff_res.text,"html.parser")

            staff_name_list = []
            staff_work_list = []

            staff_info_soup = staff_soup.find_all('span',{'class':'name'})

            for each_staff in staff_info_soup:
                staff_name_list.append(str(each_staff.a.text).strip)
                staff_work = str(each_staff.find_next_siblings().text)
                staff_work_list.append(staff_work)

            staff_dic = dict(zip(staff_name_list,staff_work_list))
            content_list.append(staff_dic)
            time.sleep(0.2)

            book_dic = dict(zip(tag_list,content_list))
            all_dic.append(book_dic)
            
            use_time = time.time() - start_time
            print('\tuse_time:{}s'.format(str(use_time)))

            time.sleep(3)
        except: 
            continue
        

    with open('book.json','w',encoding='utf-8') as fp:
        movie_json['电影'] = all_dic
        json.dump(movie_json,fp,ensure_ascii=False)


def main():
    movie_crawl()
    book_crawl()

if __name__ == '__main__':
    main()
