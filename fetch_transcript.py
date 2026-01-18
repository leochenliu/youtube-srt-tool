import yt_dlp
import os
import sys

def run(video_url):
    # 将 Secret 中的内容写入临时文件供 yt-dlp 使用
    cookie_file = 'cookies_temp.txt'
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hans', 'en'],
        'cookiefile': cookie_file,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'transcript')
            
            # 保存结果到 result.txt
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write(f"标题: {title}\n链接: {video_url}\n\n")
                if 'subtitles' in info or 'automatic_captions' in info:
                    f.write("已成功提取字幕信息，请在 Artifacts 中查看下载。")
                else:
                    f.write("未找到字幕。")
            print("任务完成！")
    except Exception as e:
        print(f"出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    url = sys.argv[1]
    run(url)
