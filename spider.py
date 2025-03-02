import requests
from bs4 import BeautifulSoup

def get_page_title(url):
    try:
        # 设置请求头（如User-Agent）来模拟浏览器行为，降低被识别为爬虫的概率
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        # 发送HTTP请求获取网页内容
        #response = requests.get(url)
        # 检查响应状态码，确保请求成功
        response.raise_for_status()
        # 设置响应内容的编码
        response.encoding = response.apparent_encoding
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找网页标题
        title = soup.title.string
        return title
    except requests.RequestException as e:
        print(f"请求出错: {e}")
    except Exception as e:
        print(f"发生其他错误: {e}")
    return None

if __name__ == "__main__":
    # 要爬取的网页URL
    url = "https://note.youdao.com/web/#/file/D24D9664401F42C89C902D8FA8B822D0/note/WEB7e268ee3e16f4428b8eb8e734347eecf/"  # 请将此URL替换为你要爬取的实际URL
    # https://www.bilibili.com/video/BV1DkwYegEPS/?spm_id_from=333.1007.tianma.4-2-12.click&vd_source=80cd7231c45aa66cfa15eff2ab3cacd0
    title = get_page_title(url)
    if title:
        print(f"网页标题: {title}")