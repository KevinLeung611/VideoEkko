import subprocess

def extract_audio(video_file: str, output_file: str):
    try:
        print(f"Executing command: ffmpeg -i {video_file} -vn -acodec pcm_s16le -ar 44100 -ac 2 {output_file + ".wav"}")

        subprocess.run(
            ["ffmpeg", "-i", video_file, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", output_file + ".wav", "-y"],
            check=True)

        return output_file + ".wav"
    except subprocess.CalledProcessError as e:
        print(f"Extracting audio failed: {e}")

def merge_subtitle(video_file: str, subtitle_file: str, output_file: str):
    cmd = ["ffmpeg", "-i", video_file, "-vf",
           f"subtitles={subtitle_file}:force_style='FontName=Yuanti SC,FontSize=12,PrimaryColour=&HFFFFFF,Outline=1,OutlineColour=&H000000'",
           "-c:a", "copy", output_file, "-y"]
    subprocess.run(cmd, text=True)

