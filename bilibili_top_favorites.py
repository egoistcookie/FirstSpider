import requests
import json
import time
from prettytable import PrettyTable
from datetime import datetime
import sys
import random

def get_popular_videos(ps=20, pn=1, max_retries=3):
    """
    获取B站热门视频
    ps: 每页视频数量
    pn: 页码
    max_retries: 最大重试次数
    """
    # 使用排行榜API
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
            # 随机延迟1-2秒
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                return data
            else:
                print(f"API返回错误代码: {data.get('code')}, 消息: {data.get('message')}")
        except requests.RequestException as e:
            if retry == max_retries - 1:
                print(f"获取数据失败: {e}")
                return None
            print(f"重试获取数据 (尝试 {retry + 2}/{max_retries})...")
            time.sleep(2)  # 重试前等待2秒
    return None

def format_timestamp(timestamp):
    """将时间戳转换为可读格式"""
    try:
        # B站时间戳似乎有问题，我们暂时只显示相对时间
        current_time = int(time.time())
        diff = current_time - timestamp
        
        if diff < 0:  # 如果时间戳在未来
            return "最近发布"
            
        if diff < 3600:  # 1小时内
            return f"{diff // 60}分钟前"
        elif diff < 86400:  # 24小时内
            return f"{diff // 3600}小时前"
        elif diff < 2592000:  # 30天内
            return f"{diff // 86400}天前"
        else:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return "时间未知"

def format_number(num):
    """格式化数字，添加千位分隔符"""
    return "{:,}".format(num)

def main():
    try:
        # 创建表格对象来格式化输出
        table = PrettyTable()
        table.field_names = ["序号", "标题", "作者", "发布时间", "收藏数", "播放量", "视频地址"]
        table.max_width = 50  # 设置最大列宽

        print("正在获取B站热门视频信息...")
        
        data = get_popular_videos()
        if not data or 'data' not in data or 'list' not in data['data']:
            print("未能获取到视频数据")
            return

        videos = data['data']['list']
        
        # 按收藏数排序
        videos.sort(key=lambda x: x['stat']['favorite'], reverse=True)
        
        # 只取前100个视频
        videos = videos[:100]

        # 在控制台输出获取到的视频数量，告知用户成功获取了多少个视频数据
        # 这有助于用户了解程序执行进度和数据获取状态
        print(f"\n成功获取到 {len(videos)} 个视频的数据")

        # 将数据添加到表格
        for i, video in enumerate(videos, 1):
            try:
                title = video['title']
                author = video['owner']['name']
                publish_time = format_timestamp(video['pubdate'])
                favorites = format_number(video['stat']['favorite'])
                view_count = format_number(video['stat']['view'])
                # 构建视频的完整URL地址，使用视频的bvid（B站视频唯一标识符）
                # 这样用户可以通过这个链接直接访问到对应的视频页面
                video_url = f"https://www.bilibili.com/video/{video['bvid']}"
                
                # 处理过长的文本
                if len(title) > 50:
                    title = title[:47] + "..."
                if len(author) > 20:
                    author = author[:17] + "..."
                    
                table.add_row([i, title, author, publish_time, favorites, view_count, video_url])
            except Exception as e:
                print(f"处理第{i}个视频数据时出错: {e}")
                continue

        # 保存数据到文件
        with open('bilibili_top100.txt', 'w', encoding='utf-8') as f:
            f.write(table.get_string())
            
        print("\n数据已保存到 bilibili_top100.txt")
        print("\n前10个视频信息预览：")
        print(table[:10])

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 