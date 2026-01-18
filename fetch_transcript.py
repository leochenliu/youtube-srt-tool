import yt_dlp
import os
import sys
import requests

def run(video_url):
    cookie_file = 'cookies_temp.txt'
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,         # 检查手动上传字幕
        'writeautomaticsub': True,     # 强制检查自动生成字幕
        'subtitleslangs': ['zh.*', 'en'], # 使用通配符抓取所有中文变体
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("正在深度扫描字幕...")
            info = ydl.extract_info(video_url, download=False)
            
            # 整合所有可能的字幕来源
            all_subs = {**info.get('subtitles', {}), **info.get('automatic_captions', {})}
            
            # 筛选出所有中文相关的 Key (如 zh-Hans, zh-Hant, zh-TW, zh 等)
            zh_keys = [k for k in all_subs.keys() if k.startswith('zh')]
            
            target_key = None
            if zh_keys:
                target_key = zh_keys[0] # 取找到的第一个中文版本
                print(f"找到中文标签: {target_key}")
            elif 'en' in all_subs:
                target_key = 'en'
                print("未找到中文，回退至英文。")

            transcript_text = "未找到任何字幕轨道。请检查视频是否开启了 CC 字幕。"

            if target_key:
                sub_info = all_subs[target_key]
                # 尝试多种格式：json3 > vtt > srt
                json_url = next((s['url'] for s in sub_info if 'json3' in s.get('ext', '')), None)
                
                if json_url:
                    resp = requests.get(json_url)
                    if resp.status_code == 200:
                        data = resp.json()
                        lines = []
                        for event in data.get('events', []):
                            if 'segs' in event:
                                text = "".join([s['utf8'] for s in event['segs'] if 'utf8' in s]).strip()
                                if text: lines.append(text)
                        transcript_text = "\n".join(lines)
                else:
                    transcript_text = f"找到字幕轨道但无法解析格式。下载链接: {sub_info[0]['url']}"
            
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write(f"标题: {info.get('title')}\n")
                f.write("-" * 30 + "\n")
                f.write(transcript_text)
                
            print("处理完毕。")
            
    except Exception as e:
        print(f"错误细节: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run(sys.argv[1])
