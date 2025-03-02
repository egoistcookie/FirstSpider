import requests
import json
import time
from prettytable import PrettyTable
from datetime import datetime
import sys
import random

def get_popular_videos(max_retries=3):
    """
    获取视频网站热门视频
    max_retries: 最大重试次数
    """
    url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    params = {
        "rid": 0,  # 全站
        "type": "all"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
    }

    for retry in range(max_retries):
        try:
            # 随机延迟1-2秒，避免请求过快
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                return data
            else:
                print(f"API返回错误: {data.get('code')}, 信息: {data.get('message')}")
        except requests.RequestException as e:
            if retry == max_retries - 1:
                print(f"获取数据失败: {e}")
                return None
            print(f"正在重试 ({retry + 2}/{max_retries})...")
            time.sleep(2)
    return None

def format_number(num):
    """格式化数字，添加千位分隔符"""
    return "{:,}".format(num)

def main():
    try:
        print("开始获取热门视频信息...")
        
        # 创建表格
        table = PrettyTable()
        table.field_names = ["排名", "标题", "简介", "发布时间", "播放量", "视频地址"]
        
        # 设置列宽度，避免内容过长
        table._max_width = {
            "标题": 40,
            "简介": 60,
            "发布时间": 20,
            "播放量": 15,
            "视频地址": 30
        }

        # 获取视频数据
        data = get_popular_videos()
        if not data or 'data' not in data or 'list' not in data['data']:
            print("未能获取到视频数据")
            return

        videos = data['data']['list']
        
        # 按播放量排序并获取前10个
        videos.sort(key=lambda x: x['stat']['view'], reverse=True)
        top_videos = videos[:10]

        print(f"\n成功获取到前 {len(top_videos)} 个热门视频")

        # 处理每个视频的数据
        for rank, video in enumerate(top_videos, 1):
            try:
                title = video['title']
                desc = video['desc']
                publish_time = datetime.fromtimestamp(video['pubdate']).strftime('%Y-%m-%d %H:%M')
                view_count = format_number(video['stat']['view'])
                video_url = f"https://www.bilibili.com/video/{video['bvid']}"

                # 处理过长的文本
                if len(title) > 40:
                    title = title[:37] + "..."
                if len(desc) > 60:
                    desc = desc[:57] + "..."

                table.add_row([rank, title, desc, publish_time, view_count, video_url])
            except Exception as e:
                print(f"处理第{rank}个视频时出错: {e}")
                continue

        # 保存结果到文件
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'hot_videos_top10_{current_time}.txt'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("获取时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            f.write(table.get_string())

        print(f"\n数据已保存到 {filename}")
        print("\n热门视频TOP10：")
        print(table)

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 