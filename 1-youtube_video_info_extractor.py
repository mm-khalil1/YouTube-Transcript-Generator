import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

input_file = "./video_url_list.csv"      # File containing URLs only, each URL in a separate line
output_file = "./videos_info.csv"    # Desired name of the file where info will be stored

def convert_short_youtube_url(short_url):
    """Converts a shortened YouTube URL to the full-length format."""
    if "youtu.be" in short_url:
        # Split by 'youtu.be/' to extract the video ID
        video_id = short_url.split("youtu.be/")[-1]
        # Split by '?' in case there's a query string
        video_id = video_id.split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return short_url  # Return unchanged if not a shortened YouTube URL

def clean_url(url):
    """Cleans up a URL by removing everything after the '&' character."""
    url = convert_short_youtube_url(url)
    url_parts = url.split("&")
    return url_parts[0].strip()

def get_date_published(soup):
    """Extracts date published of a video from the HTML soup."""
    date_published_meta = soup.find("meta", itemprop="datePublished")
    if date_published_meta:
        date_published = date_published_meta.get("content")
        return datetime.strptime(date_published, "%Y-%m-%dT%H:%M:%S%z").strftime("%d-%m-%Y")
    return None

def get_title(soup):
    """Extract title of a video from HTML soup."""
    video_title_meta = soup.find("meta", itemprop="name")
    return video_title_meta.get("content") if video_title_meta else None

def get_video_ID(soup):
    """Extract ID of a video from HTML soup."""
    video_ID_meta = soup.find("meta", itemprop="identifier")
    return video_ID_meta.get("content") if video_ID_meta else None

def get_duration(soup):
    """Extracts the duration of a video from the HTML soup."""
    duration_meta = soup.find("meta", itemprop="duration")
    if duration_meta:
        duration_str = duration_meta.get("content")
        minutes = int(duration_str.split("M")[0][2:])
        seconds = int(duration_str.split("M")[1].split("S")[0])
        hours, minutes = divmod(minutes, 60)
        duration = f"{hours}:{minutes:02}:{seconds:02}" if hours > 0 else f"{minutes}:{seconds:02}"
        duration_sec = hours * 3600 + minutes * 60 + seconds
        return duration, duration_sec
    return None

def get_video_info(url):
    """Scrapes video information from a given URL."""
    try:
        # Check if the URL is a valid YouTube video URL
        if "youtube.com/watch" not in url:
            raise ValueError("Invalid YouTube video URL.")
        
        # Request video page
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract video information
        video_ID = get_video_ID(soup)
        video_title = get_title(soup)
        date_published = get_date_published(soup)
        duration = get_duration(soup)

        # Check if all required information is present
        if all([video_title, video_ID, date_published, duration]):
            return {
                'Video ID': video_ID,
                'Video Title': video_title,
                'Date Published': date_published,
                'Duration': duration[0],
                'Duration (sec)': duration[1]
            }
        else:
            return None

    except ValueError as ve:
        raise ve
    except requests.RequestException as re:
        raise Exception("Error occurred during request:", re)
    except Exception as e:
        raise Exception("An error occurred during scraping:", e)

def is_valid_youtube_url(url):
    """Checks if the given URL is a valid YouTube video URL."""
    if "youtube.com/watch" in url or "youtu.be" in url:
        return True
    return False

def read_urls_from_csv(input_file):
    """Reads URLs from an input CSV file."""
    valid_urls = []
    try:
        with open(input_file, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Check if the URL in the row is a valid YouTube URL
                if row and is_valid_youtube_url(row[0]):
                    valid_urls.append(row[0])
        return valid_urls
    except FileNotFoundError:
        print("Error: Input file not found.")
        return []

def write_video_info_to_csv(video_info_list, output_file, fieldnames):
    """Writes video information to an output CSV file."""
    try:
        with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write header if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()
            # Write video information
            writer.writerows(video_info_list)
        print("Videos Information have been extracted and exported to", output_file)
    except Exception as e:
        print(f"Error: {e}")

def scrape_and_write_video_info(input_file, output_file):
    """Reads URLs from an input CSV file, scrapes video information, and writes to an output CSV file."""
    urls = read_urls_from_csv(input_file)

    # Define fieldnames for the output CSV file
    fieldnames = ['Number', 'Video ID', 'URL', 'Video Title', 'Date Published', 'Duration', 'Duration (sec)']

    video_info_list = []

    # Iterate over each URL and scrape video information
    for number, url in enumerate(urls, start=1):
        # Scrape video information
        video_info = get_video_info(url)
        if video_info:
            cleaned_url = clean_url(url)

            # Add additional fields to the video information
            video_info['URL'] = cleaned_url
            video_info['Number'] = number

            # Add video information to the list
            video_info_list.append(video_info)

            # Print progress every 20 iterations
            if number % 10 == 0:
                print(f"Finished processing video number: {number}")

    # Write video information to the output CSV file
    write_video_info_to_csv(video_info_list, output_file, fieldnames)

if __name__ == "__main__":
    # Scrape video information from URLs and write to CSV
    scrape_and_write_video_info(input_file, output_file)
