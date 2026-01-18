import yt_dlp
import os
import sys
import glob
import re

def sanitize_filename(filename):
    """
    清洗文件名，移除 Windows/Linux 不允许的特殊字符
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def clean_subtitle_text(text):
    """
    清洗字幕内容：移除 HTML 标签、时间戳和重复行
    """
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'(?m)^(\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3}).*\n?', '', text)
    text = re.sub(r'(?m)^(WEBVTT|Kind:|Language:|NOTE|STYLE).*\n?', '', text)
    text = re.sub(r'(?m)^\d+$\n?', '', text)
    
    lines = text.splitlines()
    final_lines = []
    for line in lines:
        line = line.strip()
        if line and (not final_lines or line != final_lines[-1]):
            final_lines.append(line)
            
    return "\n".join(final_lines)

def run(video_url):
    output_prefix = 'temp_sub_output'
    cookie_file = 'cookies.txt'
    
    if not os.path.exists(cookie_file):
        print(f"错误: 找不到 {cookie_file}！请先导出 Cookie 文件到此文件夹。")
        return

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hant', 'zh-Hans', 'zh.*', 'en'],
        'cookiefile': cookie_file,
        'outtmpl': f'{output_prefix}.%(ext)s',
        'allow_unplayable_formats': True,
        'ignore_no_formats_error': True,
        'quiet': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        # 清理旧的临时文件
        for f in glob.glob(f"{output_prefix}*"):
            os.remove(f)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"--- 正在提取: {video_url} ---")
            info = ydl.extract_info(video_url, download=True)
            
            # 获取视频标题并清洗为合法文件名
            video_title = info.get('title', 'Video_Transcript')
            safe_title = sanitize_filename(video_title)
            final_filename = f"{safe_title}.txt"
            
            # 定位下载的字幕文件
            subtitle_files = glob.glob(f"{output_prefix}*")
            
            if subtitle_files:
                target_file = subtitle_files[0]
                print(f"找到字幕文件: {target_file}")
                
                with open(target_file, 'r', encoding='utf-8') as f_in:
                    raw_content = f_in.read()
                
                # 清洗并保存到以视频标题命名的文件
                clean_content = clean_subtitle_text(raw_content)
                
                with open(final_filename, 'w', encoding='utf-8') as f_out:
                    f_out.write(f"标题: {video_title}\n")
                    f_out.write(f"链接: {video_url}\n")
                    f_out.write("="*30 + "\n\n")
                    f_out.write(clean_content)
                
                print(f"\n成功！文稿已保存至: {final_filename}")
                
                # 清理产生的临时字幕文件
                os.remove(target_file)
            else:
                print("\n失败: 未能生成字幕文件。请检查该视频是否支持 CC 字幕。")

    except Exception as e:
        print(f"\n运行发生错误: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python fetch_transcript.py <youtube_url>")
    else:
        run(sys.argv[1])
