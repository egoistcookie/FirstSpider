import requests
import json
import time
from prettytable import PrettyTable
from datetime import datetime

def get_popular_videos(ps=20, pn=1):
    """
    获取B站热门视频
    ps: 每页视频数量
    pn: 页码
    """
    url = "https://api.bilibili.com/x/web-interface/popular"
    params = {
        "ps": ps,
        "pn": pn,
        "order_by": "favorite"  # 按收藏量排序
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取数据时出错: {e}")
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
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception as e:
        return "时间未知"

def format_number(num):
    """格式化数字，添加千位分隔符"""
    return "{:,}".format(num)

def main():
    # 创建表格对象来格式化输出
    table = PrettyTable()
    table.field_names = ["序号", "标题", "作者", "发布时间", "收藏数", "播放量", "视频地址"]
    table.max_width = 50  # 设置最大列宽

    videos = []
    pages_needed = 5  # 每页20个视频，需要5页来获取100个视频
    
    print("正在获取B站收藏量前100的视频信息...")
    
    for page in range(1, pages_needed + 1):
        data = get_popular_videos(ps=20, pn=page)
        if data and data['code'] == 0:
            videos.extend(data['data']['list'])
            print(f"已获取第{page}页数据...")
        else:
            print(f"获取第{page}页数据失败")
        time.sleep(1)  # 添加延迟，避免请求过于频繁

    # 按收藏数排序
    videos.sort(key=lambda x: x['stat']['favorite'], reverse=True)
    
    # 只取前100个视频
    videos = videos[:100]

    # 将数据添加到表格
    for i, video in enumerate(videos, 1):
        title = video['title']
        author = video['owner']['name']
        publish_time = format_timestamp(video['pubdate'])
        favorites = format_number(video['stat']['favorite'])
        view_count = format_number(video['stat']['view'])
        video_url = f"https://www.bilibili.com/video/{video['bvid']}"
        
        # 处理过长的文本
        if len(title) > 50:
            title = title[:47] + "..."
        if len(author) > 20:
            author = author[:17] + "..."
            
        table.add_row([i, title, author, publish_time, favorites, view_count, video_url])

    # 保存数据到文件
    with open('bilibili_top100.txt', 'w', encoding='utf-8') as f:
        f.write(table.get_string())
        
    print("\n数据已保存到 bilibili_top100.txt")
    print("\n前10个视频信息预览：")
    print(table[:10])

if __name__ == "__main__":
    main() 