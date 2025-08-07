from multiprocessing import Pool
import subprocess
import os
import sys
import ast
import pandas as pd

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
            "-ss", "00:00:01", "-vframes", "1", First_screenshot_file 
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

    print(f"Video {input_file.name} procesado.\n")

def PoolVideoCompressor(video_poolArray):
    with Pool(processes=4) as pool:
        pool.map(VideoCompressor, video_poolArray)

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