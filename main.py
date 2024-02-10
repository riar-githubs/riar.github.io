# -*- coding: utf-8 -*-
import string
import time
import re
import random
import requests
import pprint

'''
==========================================酷狗音乐解析主要API=============================================
1.get_rank_list()   获取音乐榜单列表   返回形式：（榜单名，榜单地址）
2.get_rank_info(url)  url为榜单地址 返回歌曲的信息[{}]
3.get_search_musicData(search_txt,dis_num)   search_txt：搜索内容,dis_num：总共加载几首歌曲，返回歌曲的信息[{}]
=========================================内部函数=========================================================
4.get_musicInfo(hash,id)  通过传入的hash、id 返回歌名、播放地址、图片、歌词 字典形式
返回形式：music_info_dic={'audio_name':XXXX,'play_url':XXXX,'lyrics':XXX,'img':XXX}
5.klcTolrc(self,lyrics)  通过传入获取的krc歌词   变成lrc形式的歌词
========================================================================================================
可以用主函数测试
'''


class kuGouMusic():
    def __init__(self):

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', }

    def __get_response(self, url, headers):
        res = requests.get(url, headers)
        return res

    # 获取酷狗音乐榜单
    def get_rank_list(self):
        rank_url = 'https://www.kugou.com/yy/html/rank.html'
        res = self.__get_response(rank_url, self.headers)
        res.encoding = res.apparent_encoding
        rank_list_urls = re.findall(r'<a title="(.*?)" .*? hidefocus="true" href="(.*?)"', res.text)[1:]
        return rank_list_urls

    # 获取榜单的Hash、id
    def get_rank_info(self, url):
        res = self.__get_response(url, self.headers)
        res.encoding = res.apparent_encoding
        Hash_list = re.findall('"Hash":"(.*?)"', res.text)
        album_id_list = re.findall('"album_id":(.*?),', res.text)
        play_list = []
        num = 0
        for Hash, album_id in zip(Hash_list, album_id_list):
            print(f'\r正在加歌单歌曲列表，....当前进度：{int((num + 1) / len(Hash_list) * 100)}%', end='')
            play_list.append(self.__get_musicInfo(Hash, album_id))
            num = num + 1
        return play_list

    # ======================以下是搜索部分=============#
    def get_search_musicData(self, word='任贤齐', page_mum=1):
        url = 'http://mobilecdn.kugou.com/api/v3/search/song'
        data_list = []
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        parameter = {
            'keyword': word,
            'page': page_mum,
            'pagesize': '30',
        }
        res = requests.get(url, headers=headers, params=parameter).json()
        info_list = res['data']['info']
        num = 0
        for info in info_list:
            print(f'\r正在加载搜索歌曲列表，....当前进度：{int((num + 1) / len(info_list) * 100)}%', end='')
            data_list.append(self.__get_musicInfo(info['hash'], info['album_id']))
            num = num + 1
        return data_list

    # ======================通过Hash,id获取到歌曲地址、LRC、封面、歌曲名共用部分=============#
    # 获取歌曲信息 hash 为字符串 id为整型数据
    def __get_musicInfo(self, hash, id):
        music_url = 'https://wwwapi.kugou.com/yy/index.php'
        parameter = {
            'r': 'play/getdata',
            'hash': hash,
            'dfid': self.__get_dfid(23),
            'mid': self.__get_mid(23),
            'album_id': id,
            '_': str(round(time.time() * 1000))  # 时间戳
        }
        json_data = requests.get(music_url, headers=self.headers, params=parameter).json()
        music_info_dic = {
            'audio_name': json_data['data']['audio_name'],
            'play_url': json_data['data']['play_url'],
            'lyrics': self.__klcTolrc(json_data['data']['lyrics']),
            'img_conntent': json_data['data']['img']
        }
        return music_info_dic

    # 获取a-z A-Z 0-9组成的随机23位数列
    def __get_dfid(self, num):
        random_str = ''.join(random.sample((string.ascii_letters + string.digits), num))
        return random_str

    # 获取a-z  0-9组成的随机23位数列
    def __get_mid(self, num):
        random_str = ''.join(random.sample((string.ascii_letters[:26] + string.digits), num))
        return random_str

    # krc转成lrc
    def __klcTolrc(self, lyrics):
        index = lyrics.find('[00:00')
        lyrics = lyrics[index:]
        return lyrics


if __name__ == '__main__':
    d = kuGouMusic()
    # url='https://www.kugou.com/yy/rank/home/1-8888.html?from=rank'
    # lis=d.get_rank_info(url)
    # pprint.pprint(lis)
    lis2 = d.get_search_musicData()
    print(lis2)