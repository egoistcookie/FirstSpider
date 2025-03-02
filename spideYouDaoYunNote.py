import sys
import io
import requests
from bs4 import BeautifulSoup
import re
import logging
import locale
import json
import brotli

# 强制设置系统默认编码
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 设置本地化编码
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG级别
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('spider_debug.log', encoding='utf-8'),
        # 自定义带编码的StreamHandler
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
    ]
)

# 标题格式化
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# 有道云笔记：《备忘录》篇的download请求
def get_note_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            # 'Accept': '*/*',
            'Accept-Encoding' : 'gzip,deflate,br',
            # 'Connection':'keep-alive',
            # 'Cache-Control':'no-cache',
            # 'Content-Length':'121',
            # 'Host':'note.youdao.com',
            'Cookie': 'hb_MA-B0D8-94CBE089C042_source=www.baidu.com; Hm_lvt_7fe66a8317b6d6f28c82b62b9f890118=1740893320; Hm_lpvt_7fe66a8317b6d6f28c82b62b9f890118=1740893320; HMACCOUNT=29005595904466B9; __yadk_uid=ZlRyzrbKx1IF9Hz5MMWVhDPQwjReRvFl; OUTFOX_SEARCH_USER_ID_NCOO=105754892.64450204; OUTFOX_SEARCH_USER_ID=-1177979017@163.177.223.166; YNOTE_SESS=v2|Zy5mmIFIhqBhLzf6LTuRJLhLTu0fgBReFkLYMP46uRYMO4TKOMeBRTBk4eyRfYf0Pu6LqFPMTS0q4RLeS6Mwy0QLnLgZ6MlY0; YNOTE_LOGIN=3||1740893431920; YNOTE_CSTK=tnN-LCL1'
        }
        
        session = requests.Session()
        logging.debug("="*50)
        logging.debug(f"【请求开始】URL: {url}")
        logging.debug(f"【请求头】\n{headers}")
        # 发送 get 请求
        #response = session.get(url, headers=headers)
        # 发送 POST 请求
        # 定义请求体
        data = {
            'fileId': 'WEB7e268ee3e16f4428b8eb8e734347eecf',
            'version': '-1',
            'convert': 'true',
            'editorVersion': '1714445486000',
            'editorType': '1',
            'cstk': 'tnN-LCL1',
        }

        # 将字典转换为 JSON 字符串
        json_data = json.dumps(data)
        xml_data ="fileId=WEB7e268ee3e16f4428b8eb8e734347eecf&version=-1&convert=true&editorVersion=1714445486000&editorType=1&cstk=tnN-LCL1";
        response = session.post(url, headers=headers, data=xml_data)
        
        # 检测并设置正确的编码
        if not response.encoding or response.encoding.lower() not in ['utf-8', 'utf8']:
            response.encoding = response.apparent_encoding or 'utf-8'
            logging.info(f"已设置编码为: {response.encoding}")

        if response.headers.get('Content-Encoding') == 'br':
            try:
                decoded_content = brotli.decompress(response.content)
            except brotli.error:
                logging.warning("Brotli decompression failed, using raw content")
                decoded_content = response.content
        else:
            decoded_content = response.content

        # 记录完整响应信息
        logging.debug(f"【响应状态】{response.status_code}")
        logging.debug(f"【最终URL】{response.url}")
        logging.debug(f"【最终请求体】{response.request.body}")
        logging.debug(f"【响应编码】{response.encoding}")
        logging.debug(f"【响应头】\n{response.headers}")
        logging.debug(f"【响应体大小】{len(response.text)} 字符")
        
        # 保存完整响应内容
        with open('full_response.html', 'w', encoding='utf-8') as f:
            if isinstance(decoded_content, bytes):
                # 将字节数据解码为字符串
                content_str = decoded_content.decode('utf-8')
                try:
                    # 尝试将字符串解析为 JSON 对象
                    json_data = json.loads(content_str)
                    # 提取 "5" 标签对应的内容
                    if "5" in json_data:
                        # 提取所有 "8" 标签的值
                        values = extract_values_from_json(json_data["5"])
                        # 将提取的值写入文件
                        f.write("\n".join(values))
                    else:
                        logging.warning("JSON 数据中未找到 '5' 标签")
                        f.write(content_str)  # 如果未找到 "5" 标签，写入原始内容
                except json.JSONDecodeError:
                    # 如果内容不是 JSON，直接写入原始字符串
                    f.write(content_str)
            else:
                try:
                    # 如果 decoded_content 是字符串，尝试解析为 JSON
                    json_data = json.loads(decoded_content)
                    # 提取 "5" 标签对应的内容
                    if "5" in json_data:
                        # 提取所有 "8" 标签的值
                        values = extract_values_from_json(json_data["5"])
                        # 将提取的值写入文件
                        f.write("\n".join(values))
                    else:
                        logging.warning("JSON 数据中未找到 '5' 标签")
                        f.write(decoded_content)  # 如果未找到 "5" 标签，写入原始内容
                except json.JSONDecodeError:
                    # 如果内容不是 JSON，直接写入原始字符串
                    f.write(decoded_content)
        logging.info("已保存完整响应到 full_response.html")

        response.raise_for_status()

        # 检查重定向
        if "login" in response.url.lower():
            logging.error("!!! 检测到登录重定向 !!!")
            logging.error("可能原因：1. Cookie失效 2. 需要登录 3. 权限不足")
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 调试页面结构
        logging.debug("【页面结构分析】")
        logging.debug(f"Title标签内容: {soup.title.string if soup.title else '无标题'}")
        logging.debug(f"找到的div数量: {len(soup.find_all('div'))}")
        
        # 详细标题解析
        title_tag = soup.find('div', class_='title')
        if title_tag:
            logging.debug(f"标题元素原始内容:\n{title_tag.prettify()}")
            title = title_tag.get_text(strip=True)
            logging.info(f"解析到标题: {title}")
        else:
            logging.warning("未找到标题元素，尝试备用选择器...")
            title_tag = soup.find('h1')  # 尝试其他选择器
            if title_tag:
                title = title_tag.get_text(strip=True)
                logging.info(f"备用选择器找到标题: {title}")
            else:
                title = "未命名笔记"
                logging.error("所有标题选择器均失败")

        clean_title = sanitize_filename(title)
        
        # 详细内容解析
        content_div = soup.find('div', class_='content')  # 查找包含内容的 div 元素
        if not content_div:  # 如果未找到内容区域
            logging.error("内容区域未找到，可能原因：")
            logging.error("1. 页面结构已变更 2. class名称不同 3. 内容需要登录")
            logging.debug("前500字符内容预览:\n"+response.text[:500])
            return None, None  # 返回空值表示解析失败
            
        # 内容结构分析
        logging.debug(f"内容区域找到的段落数: {len(content_div.find_all('p'))}")
        logging.debug(f"内容区域原始HTML片段:\n{content_div.prettify()[:300]}...")
        
        # 提取所有段落文本并拼接为字符串
        content = '\n'.join([p.get_text() for p in content_div.find_all('p')])
        if len(content) < 10:  # 如果提取的内容过短
            logging.warning("提取内容过短，可能包含富文本或图片内容")
            
        return clean_title, content  # 返回清理后的标题和解析的内容
        
    except requests.RequestException as e:
        logging.error("!!! 网络请求异常 !!!")
        logging.error(f"异常类型: {type(e).__name__}")
        if hasattr(e, 'request'):
            logging.error(f"请求URL: {e.request.url}")
        if hasattr(e, 'response'):
            logging.error(f"响应状态码: {e.response.status_code}")
            logging.error(f"错误响应头:\n{e.response.headers}")
            logging.error(f"错误响应体前500字符:\n{e.response.text[:500]}")
    except Exception as e:
        logging.error("!!! 未处理的异常 !!!")
        logging.error(f"异常类型: {type(e).__name__}")
        logging.error(f"异常信息: {str(e)}")
        logging.error("异常堆栈:", exc_info=True)
    return None, None

def save_note(title, content):
    if not title or not content:
        return False
        
    try:
        filename = f"{title}.txt"
        # 添加UTF-8 BOM头 \ufeff
        with open(filename, 'w', encoding='utf-8-sig', errors='ignore') as f:
            f.write('\ufeff' + content)
        logging.info(f"文件保存成功: {filename}")
        return True
    except Exception as e:
        logging.error(f"文件保存失败: {str(e)}", exc_info=True)
        return False

def extract_values_from_json(json_data):
    """
    递归提取 JSON 数据中 "5" 标签下的 "7" 标签数组中的 "8" 标签的值
    """
    values = []  # 用于存储提取的值

    if isinstance(json_data, dict):  # 如果当前是字典
        if "5" in json_data:  # 如果存在 "5" 标签
            # 递归处理 "5" 标签的内容
            values.extend(extract_values_from_json(json_data["5"]))
        if "7" in json_data:  # 如果存在 "7" 标签
            for item in json_data["7"]:  # 遍历 "7" 标签的数组
                if "8" in item:  # 如果存在 "8" 标签
                    values.append(item["8"])  # 提取 "8" 标签的值
    elif isinstance(json_data, list):  # 如果当前是列表
        for item in json_data:  # 遍历列表中的每一项
            values.extend(extract_values_from_json(item))  # 递归处理每一项

    return values

if __name__ == "__main__":
    #url = "https://note.youdao.com/web/#/file/D24D9664401F42C89C902D8FA8B822D0/note/WEB7e268ee3e16f4428b8eb8e734347eecf/"
    #url ="https://note.youdao.com/yws/api/personal/sync?method=download&_system=windows&_systemVersion=&_screenWidth=1920&_screenHeight=1080
    # &_appName=ynote&_appuser=766688366d459bceea5f67aaaf2c6124&_vendor=official-website&_launch=184&_firstTime=2025/03/02%2013:28:43
    # &_deviceId=11efb95b965437d2&_platform=web&_cityCode=430000&_cityName=&_product=YNote-Web&_version=&sev=j1&sec=v1&keyfrom=web&cstk=tnN-LCL1"
    # 有道云笔记：《备忘录》篇的download请求
    url = ("https://note.youdao.com/yws/api/personal/sync?method=download&_system=windows&_systemVersion=&_screenWidth=1920&_screenHeight=1080"
           "&_appName=ynote&_appuser=766688366d459bceea5f67aaaf2c6124&_vendor=official-website&_launch=113&_firstTime=2025/03/02%2013:28:43"
           "&_deviceId=11efb95b965437d2&_platform=web&_cityCode=430000&_cityName=&_product=YNote-Web&_version=&sev=j1&sec=v1&keyfrom=web&cstk=tnN-LCL1")
    
    logging.info("="*50)
    logging.info("开始执行爬虫程序")
    title, content = get_note_content(url)
    
    if title and content:
        save_note(title, content)
    else:
        logging.error("!!! 主流程失败 !!!")
        logging.error("可能原因：")
        logging.error("1. 网络请求失败 2. 页面解析失败 3. 权限不足")
        logging.error("请检查 spider_debug.log 和 full_response.html")