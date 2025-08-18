from multiprocessing import Pool
import subprocess
import os
import sys
import re
import ast
import tempfile
import math

def round_up_decimal(num, dec_places):
    multiplier = 10 ** dec_places
    return math.ceil(num * multiplier) / multiplier

class VideoFile:
    def __init__(self, path, folder, output_folder):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = os.path.splitext(self.name)[1].lower()
        self.folder = folder
        self.output_folder = output_folder
        self.reverse = False
        self.screenshots = False

    def __str__(self):
        return f"Video File: {self.name}, Folder: {self.folder}, Output Folder: {self.output_folder}"

def VideoCompressor(input_file):
    print(f"\nProcesando video: {input_file}")

    os.makedirs(input_file.output_folder, exist_ok=True)

    output_file = os.path.join(input_file.output_folder, f"Comp_{input_file.name}.mp4")

    black_frames = DetectBlackFrames(input_file)
    
    print(black_frames)

    if not black_frames:
        if(input_file.reverse):
            Rev_video_file = os.path.join(input_file.output_folder, f"Reversed_{input_file.name}.mp4")
            subprocess.run([
                "ffmpeg","-i",input_file.path,"-vf","reverse",Rev_video_file
            ],check=True)
            print(f"Video {input_file.name} invertido guardado como {Rev_video_file}")

        if(input_file.screenshots):
            First_screenshot_file = os.path.join(input_file.output_folder, f"PrimerFrame_{input_file.name}.jpg")
            subprocess.run([
                "ffmpeg", "-i", input_file.path,
                "-ss", "00:00:00", "-vframes", "1", First_screenshot_file 
            ], check=True)
            print(f"Primer frame guardado")
            Last_screenshot_file = os.path.join(input_file.output_folder, f"UltimoFrame_{input_file.name}.jpg")
            subprocess.run([
                "ffmpeg","-sseof","-3","-i",input_file.path,"-update","1","-q:v","1",Last_screenshot_file
            ],check=True)
            print(f"Ultimo frame guardado")

        subprocess.run([
            "ffmpeg", "-i", input_file.path,
            "-vcodec", "libx264", "-crf", "23", output_file
        ], check=True)
    else:
        print("Frames negros detectados")
        Erase_Compress_BlackFrames(input_file, black_frames)

    

    print(f"Video {input_file.name} procesado.\n")

def PoolVideoCompressor(video_poolArray):
    with Pool(processes=4) as pool:
        pool.map(VideoCompressor, video_poolArray)

def DetectBlackFrames(input_file):
    black_frames_detect =[
        "ffmpeg",
        "-hide_banner",
        "-analyzeduration", "2147483647",
        "-probesize", "2147483647",
        "-i", input_file.path,
        "-vf", f"blackdetect=d={0}:pic_th={0.70}",
        "-an",
        "-f", "null", "-"
    ]

    black_detection = subprocess.run(black_frames_detect, stderr=subprocess.PIPE, text=True)
    black_frames = re.findall(
        r"black_start:(\d+\.\d+)\s+black_end:(\d+\.\d+)\s+black_duration:(\d+\.\d+)",
        black_detection.stderr
    )
    black_frames = [
        {"start": float(s), "end": float(e) + 0.1, "duration": round_up_decimal(float(d),2)}
        for s, e, d in black_frames
    ]
    last_match = re.findall(
        r"black_start:(\d+\.\d+)", black_detection.stderr
    )
    if last_match:
        last_start = float(last_match[-1])
        if not any(seg["start"] == last_start for seg in black_frames):
            video_duration = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", input_file.path],
                stdout=subprocess.PIPE, text=True
            ).stdout.strip())
            black_frames.append({
                "start": last_start,
                "end": video_duration,
                "duration": video_duration - last_start
            })

    return black_frames

def Erase_Compress_BlackFrames(input_file,black_frames):
    temp_list_path = tempfile.mktemp(suffix=".txt")
    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_file.path],
        stdout=subprocess.PIPE, text=True
    ).stdout.strip())

    keep_segments = []
    last_end = 0.0
    for seg in black_frames:
        if last_end < seg["start"]:
            keep_segments.append((last_end, seg["start"]))
        last_end = seg["end"]
    if last_end < duration:
        keep_segments.append((last_end, duration))

    temp_files = []
    for i, (start, end) in enumerate(keep_segments):
        temp_file = tempfile.mktemp(suffix=".mp4")
        subprocess.run([
            "ffmpeg", "-i", input_file.path, "-ss", str(start), "-to", str(end),
            "-c:v", "libx264", "-crf", "23",
            "-c:a", "copy", temp_file
        ], check=True)
        temp_files.append(temp_file)

    with open(temp_list_path, "w") as f:
        for tf in temp_files:
            f.write(f"file '{tf}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", temp_list_path,
        "-c:v", "libx264", "-crf", "23",  
        "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        os.path.join(input_file.output_folder, f"Comp_{input_file.name}.mp4")
    ], check=True)

    if(input_file.reverse):
        Rev_video_file = os.path.join(input_file.output_folder, f"Reversed_{input_file.name}.mp4")
        subprocess.run([
            "ffmpeg","-i",os.path.join(input_file.output_folder, f"Comp_{input_file.name}.mp4"),"-vf","reverse",Rev_video_file
        ],check=True)
        print(f"Video {input_file.name} invertido guardado como {Rev_video_file}")

    if(input_file.screenshots):
        First_screenshot_file = os.path.join(input_file.output_folder, f"PrimerFrame_{input_file.name}.jpg")
        subprocess.run([
            "ffmpeg", "-i", os.path.join(input_file.output_folder, f"Comp_{input_file.name}.mp4"),
            "-ss", "00:00:00", "-vframes", "1", First_screenshot_file 
        ], check=True)
        print(f"Primer frame guardado")
        Last_screenshot_file = os.path.join(input_file.output_folder, f"UltimoFrame_{input_file.name}.jpg")
        subprocess.run([
            "ffmpeg","-sseof","-3","-i",os.path.join(input_file.output_folder, f"Comp_{input_file.name}.mp4"),"-update","1","-q:v","1",Last_screenshot_file
        ],check=True)
        print(f"Ultimo frame guardado")

    os.remove(temp_list_path)
    for tf in temp_files:
        os.remove(tf)

if __name__ == '__main__':
    video_poolArray =[]

    if len(sys.argv) > 1:
        arg_str = sys.argv[1]
        arguments = ast.literal_eval(arg_str)

        if isinstance(arguments, dict):
            arguments = [arguments]

        for videos in arguments:
            for i,path in enumerate(videos['paths']):
                newVideoFile = VideoFile(
                    path,
                    folder=os.path.dirname(path),
                    output_folder=os.path.join(os.path.dirname(path), "EDITADOS")
                    )
                print(videos['reverse'][i])
                newVideoFile.reverse = videos['reverse'][i]
                print(videos['screenshots'][i])
                newVideoFile.screenshots = videos['screenshots'][i]
                video_poolArray.append(newVideoFile)
        PoolVideoCompressor(video_poolArray)