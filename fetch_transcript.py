import yt_dlp
import os
import sys

def run(video_url):
    cookie_file = 'cookies_temp.txt'
    # 定义临时字幕文件名前缀
    output_temp = 'temp_sub'
    
    ydl_opts = {
        'skip_download': True,        # 不下载视频
        'writesubtitles': True,       # 下载手动字幕
        'writeautomaticsub': True,    # 下载自动字幕
        'subtitleslangs': ['zh.*', 'en'], # 匹配中文
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        'outtmpl': output_temp,       # 设定输出文件名
        # 核心设置：强制将字幕转换成纯文本格式 (srt)
        'postprocessors': [{
            'key': 'FFmpegSubtitlesConvertor',
            'format': 'srt',
        }],
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("正在调用 yt-dlp 下载并转换字幕...")
            ydl.download([video_url])
            
            # yt-dlp 会生成类似 temp_sub.zh-Hant.srt 的文件
            # 我们寻找生成的 srt 文件并合并到 result.txt
            files = os.listdir('.')
            srt_files = [f for f in files if f.endswith('.srt')]
            
            if srt_files:
                target_srt = srt_files[0]
                print(f"解析到字幕文件: {target_srt}")
                with open(target_srt, 'r', encoding='utf-8') as f_in:
                    content = f_in.read()
                
                # 简单清理一下 SRT 的时间轴，只保留文字（可选）
                import re
                clean_text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
                
                with open('result.txt', 'w', encoding='utf-8') as f_out:
                    f_out.write(f"视频链接: {video_url}\n")
                    f_out.write("-" * 30 + "\n")
                    f_out.write(clean_text)
                print("成功将字幕存入 result.txt")
            else:
                with open('result.txt', 'w', encoding='utf-8') as f_out:
                    f_out.write("未能在输出中找到任何生成的字幕文件。")
                print("未能生成字幕。")
                
    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run(sys.argv[1])
