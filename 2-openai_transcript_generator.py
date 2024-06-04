"""
This script fetches YouTube video information from a CSV file, downloads the audio tracks of the videos,
transcribes them using an OpenAI language model, and saves the transcriptions as text files.

Dependencies:

- whisper: A library for using OpenAI's GPT models.
- yt_dlp: A tool to download videos and extract audio from YouTube.
- pandas: A data manipulation library.
- torch: PyTorch library.
- os: Operating system functionality.

Usage:

1. Ensure dependencies are installed: whisper, yt_dlp, pandas, torch.
2. Prepare a CSV file containing information about YouTube videos (e.g., 'videos_info.csv').
3. Set the desired model size ('tiny', 'base', 'small', 'medium', 'large') and other configuration options.
4. Run the script.

"""
import whisper
import yt_dlp
import pandas as pd
import torch
import os

# Configuration
videos_info_file = "videos_info.csv"    # CSV file containing video information
model_size = "medium"           # Size of the model ("tiny", "base", "small", "medium", "large")

fetch_description = False       # Whether to fetch video description
hide_verbose = True             # Whether to hide download verbosity
start_video_id = ""             # Specify the video ID to start with from the list of IDs in the file
                                # Useful if started before and transcription was interrupted, and would like to continue from where it stopped

# Model sizes mapping
model_sizes = {
    "tiny": "tiny.en",
    "base": "base.en",
    "small": "small.en",
    "medium": "medium.en",
    "large": "large.en"     # Multilingual. Not recommended for only-English transcription
}

def load_model(model_size, device=None):
    """
    Load the Whisper model based on the specified size.

    Parameters:
        model_size (str): Size of the model ("tiny", "base", "small", "medium", "large").
        device (str, optional): Device to load the model on ("cuda" or "cpu").

    Returns:
        Whisper model: Loaded model.

    Raises:
        ValueError: If an invalid model size is provided.
    """
    model_name = model_sizes.get(model_size)
    if model_name:
        return whisper.load_model(model_name, device=device)
    else:
        raise ValueError("Invalid model size. Please choose from: 'tiny', 'base', 'small', 'medium', 'large'.")

def get_OpenAI_transcript(model_size, video_id, fetch_description, hide_verbose):
    """
    Transcribe the audio track of a YouTube video using an OpenAI Whisper.

    Parameters:
        model_size (str): Size of the model ("tiny", "base", "small", "medium", "large").
        video_id (str): YouTube video ID.
        fetch_description (bool): Whether to fetch video descriptions.
        hide_verbose (bool): Whether to hide download verbosity.
    """
    # Return if any file name contains the video_id (transcribed already)
    if any(video_id in file_name for file_name in os.listdir('.')):
        print("Video ID is in at least one file name.")
        return

    # YouTube downloader options
    ydl_opts = {
        "format": "bestaudio/best",
        "writedescription": fetch_description,
        "quiet": hide_verbose,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": f"%(title)s {video_id}.%(ext)s",
    }

    # Download and extract audio from YouTube video
    url = "https://www.youtube.com/watch?v=" + video_id
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except yt_dlp.utils.ExtractorError as e:
            print("Error: Age-restricted: ", e)
            return
        except yt_dlp.utils.DownloadError as e:
            print("Error: Unable to download: ", e)
            return

    # Get the path of the downloaded audio file
    file_path = ydl.prepare_filename(ydl.extract_info(url, download=False))
    file_path = file_path.replace(".webm", ".mp3")
    file_path = file_path.replace(".m4a", ".mp3")

    # Load the model
    model = load_model(model_size, device="cuda" if torch.cuda.is_available() else "cpu")

    # Transcribe audio using the model
    result = model.transcribe(file_path)
    text = result["text"].replace("\n", " ").strip()

    # Save transcription as text file
    name = "".join(file_path)
    name = name.replace(".mp3", ".txt")
    with open(name, "w") as file:
        file.write(text)

    print(f"############# Done video: {name} #############")

def videos_to_transcribe(df, start_video_id=""):
    """
    Generate a list of video IDs to transcribe.

    Parameters:
        df (DataFrame): DataFrame containing video information.
        start_video_id (str): Video ID from which to start transcription.

    Returns:
        list: List of video IDs to transcribe.
    """
    ids_to_transcribe = []
    
    if "Video ID" in df.columns:
        start_index = 0
        
        # Check if start_video_id is provided and "Video ID" column is not empty
        if start_video_id != "" and not df["Video ID"].empty:
            start_index = df[df["Video ID"] == start_video_id].index[0]

        # Iterate through DataFrame rows and append video IDs
        for index, row in df.iterrows():
            if index >= start_index:
                # Check if "Video ID" exists in the current row
                if "Video ID" in row and not pd.isnull(row["Video ID"]):
                    ids_to_transcribe.append(row["Video ID"])
                else:
                    print(f"Warning: No 'Video ID' found in row {index}")

    else:
        print("Error: 'Video ID' column not found in DataFrame.")
    
    return ids_to_transcribe

def delete_mp3_files(directory):
    """
    Delete all .mp3 files in the specified directory.

    Parameters:
        directory (str): Directory path.
    """
    files_in_dir = os.listdir(directory)
    mp3_files = [file for file in files_in_dir if file.endswith(".mp3")]

    for mp3_file in mp3_files:
        mp3_file_path = os.path.join(directory, mp3_file)
        os.remove(mp3_file_path)
        print(f"File '{mp3_file}' has been removed.")

if __name__ == "__main__":
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device = ", DEVICE)

    # Read video information from CSV
    videos_info_df = pd.read_csv(videos_info_file)

    # Generate list of video IDs to transcribe
    ids_to_transcribe = videos_to_transcribe(videos_info_df, start_video_id=start_video_id)

    # Transcribe each video
    for video_id in ids_to_transcribe:
        print("Started with video ID:", video_id)
        get_OpenAI_transcript(model_size, video_id, fetch_description, hide_verbose)

    # Delete .mp3 files
    current_directory = os.getcwd()  # Get current directory
    delete_mp3_files(current_directory)  # Delete .mp3 files in the current directory
