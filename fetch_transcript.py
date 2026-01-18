import yt_dlp
import os
import sys
import requests

def run(video_url):
    cookie_file = 'cookies_temp.txt'
    
    # 配置 yt-dlp 寻找中文或英文字幕
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hans', 'zh-CN', 'en'],
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("正在获取视频元数据...")
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'transcript')
            
            # 1. 尝试寻找手动上传的字幕或自动生成的字幕
            subtitles = info.get('subtitles') or info.get('automatic_captions')
            
            transcript_text = "未找到合适的字幕内容。"
            
            if subtitles:
                # 优先寻找中文，其次英文
                target_lang = None
                for lang in ['zh-Hans', 'zh-CN', 'en']:
                    if lang in subtitles:
                        target_lang = lang
                        break
                
                if target_lang:
                    # 获取字幕文件的 JSON 格式 URL (json3 格式最容易解析)
                    sub_info = subtitles[target_lang]
                    json_url = next((s['url'] for s in sub_info if s.get('ext') == 'json3'), None)
                    
                    if not json_url:
                        # 如果没有 json3，取第一个可用的格式
                        json_url = sub_info[0]['url']

                    print(f"正在抓取 {target_lang} 字幕内容...")
                    resp = requests.get(json_url)
                    if resp.status_code == 200:
                        # 简单清理一下 JSON 里的文字
                        data = resp.json()
                        lines = []
                        for event in data.get('events', []):
                            if 'segs' in event:
                                text = "".join([s['utf8'] for s in event['segs'] if 'utf8' in s]).strip()
                                if text:
                                    lines.append(text)
                        transcript_text = "\n".join(lines)
            
            # 2. 保存到结果文件
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write(f"标题: {title}\n")
                f.write(f"链接: {video_url}\n")
                f.write("-" * 30 + "\n")
                f.write(transcript_text)
                
            print("处理成功！内容已写入 result.txt")
            
    except Exception as e:
        print(f"出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误: 请提供视频 URL")
        sys.exit(1)
    run(sys.argv[1])
