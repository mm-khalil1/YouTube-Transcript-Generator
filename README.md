# YouTube Transcript Generator

This folder contains scripts and files for generating transcripts from YouTube videos.

## Files

- **0-videos_url_list.csv**

  - CSV file containing URLs of YouTube videos to be transcribed.

- **1-youtube_video_info_extractor.py**

  - Python script to extract information (such as title, date published, duration) from YouTube videos specified in the input CSV file.

- **2-openai_transcript_generator.py**

  - Python script to transcribe audio tracks of YouTube videos using OpenAI's Whisper model.

- **3-filtering_OpenAI_transcript_dataset.ipynb**
  - Jupyter notebook for filtering and processing the transcribed transcripts obtained from OpenAI's Whisper model.

## 1-youtube_video_info_extractor.py

This script extracts information from YouTube videos such as video title, date published, and duration. It reads the video URLs from the input CSV file (`video_url_list.csv`), scrapes information from each video's webpage, and exports the information to a CSV file (`videos_info.csv`).

## 2-openai_transcript_generator.py

This script transcribes the audio tracks of YouTube videos using OpenAI's Whisper model. It downloads the audio for each YouTube video, transcribes it using the specified Whisper model size, and saves the transcriptions as text files.
Run the following commands to install necessary libraries:

```bash
!pip uninstall whisper

!pip -qU install git+https://github.com/yt-dlp/yt-dlp.git
!pip -qU install git+https://github.com/openai/whisper.git
!pip -qU install torch
```

## 3-filtering_OpenAI_transcript_dataset.ipynb

This Jupyter notebook contains code for filtering and processing the transcribed transcripts obtained from OpenAI's Whisper model. It provides tools for cleaning and organizing the transcripts for further analysis.

Please make sure to provide the necessary input files and configurations before running the scripts.
