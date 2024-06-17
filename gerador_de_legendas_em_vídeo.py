import os
import subprocess
import whisper
from googletrans import Translator
from moviepy.editor import VideoFileClip
import tkinter as tk
from tkinter import filedialog, messagebox

# Funções de processamento
def extract_audio(video_path, audio_path):
    command = f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path}"
    subprocess.call(command, shell=True)

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def translate_text(text, dest_language='pt'):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

def create_srt(transcription, output_srt):
    with open(output_srt, 'w') as f:
        for i, line in enumerate(transcription.split('\n')):
            f.write(f"{i+1}\n")
            f.write("00:00:00,000 --> 00:00:05,000\n")  # Adicionar timestamps reais
            f.write(line + "\n\n")

def add_subtitles(video_path, srt_path, output_path):
    command = f"ffmpeg -i {video_path} -vf subtitles={srt_path} {output_path}"
    subprocess.call(command, shell=True)

# Funções da interface gráfica
def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
    if video_path:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, video_path)

def process_video():
    video_path = video_entry.get()
    if not video_path:
        messagebox.showerror("Erro", "Selecione um arquivo de vídeo primeiro.")
        return
    
    audio_path = "audio.wav"
    srt_path = "subtitles.srt"
    output_video_path = "video_with_subtitles.mp4"

    try:
        status_label.config(text="Extraindo áudio...")
        root.update_idletasks()
        extract_audio(video_path, audio_path)

        status_label.config(text="Transcrevendo áudio...")
        root.update_idletasks()
        transcription = transcribe_audio(audio_path)

        status_label.config(text="Traduzindo transcrição...")
        root.update_idletasks()
        translated_text = translate_text(transcription)

        status_label.config(text="Criando arquivo de legendas...")
        root.update_idletasks()
        create_srt(translated_text, srt_path)

        status_label.config(text="Adicionando legendas ao vídeo...")
        root.update_idletasks()
        add_subtitles(video_path, srt_path, output_video_path)

        status_label.config(text="Processo concluído!")
        messagebox.showinfo("Sucesso", "O vídeo com legendas foi criado com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        status_label.config(text="Erro durante o processamento.")

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Adicionar Legendas ao Vídeo")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

video_label = tk.Label(frame, text="Arquivo de vídeo:")
video_label.grid(row=0, column=0, sticky="e")

video_entry = tk.Entry(frame, width=50)
video_entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(frame, text="Selecionar", command=select_video)
browse_button.grid(row=0, column=2, padx=5, pady=5)

process_button = tk.Button(frame, text="Processar Vídeo", command=process_video)
process_button.grid(row=1, columnspan=3, pady=10)

status_label = tk.Label(frame, text="")
status_label.grid(row=2, columnspan=3)

root.mainloop()