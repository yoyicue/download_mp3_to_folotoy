import os
import requests
from flask import Flask, send_file, abort, request
from urllib.parse import urlparse

app = Flask(__name__)

# Directory for storing downloaded MP3 files
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download')
def download_mp3():
    # Get the URL from the query parameter
    mp3_url = request.args.get('url')
    if not mp3_url:
        abort(400, 'No URL provided')

    # Simple validation to check if the URL is valid
    parsed_url = urlparse(mp3_url)
    if not (parsed_url.scheme and parsed_url.netloc):
        abort(400, 'Invalid URL provided')

    # Check if the URL is from the 126.net domain
    if '126.net' not in parsed_url.netloc:
        abort(400, 'URL does not belong to the 126.net domain')

    # Extract the file name from the URL or generate one
    mp3_filename = os.path.basename(parsed_url.path)
    if not mp3_filename.endswith('.mp3'):
        abort(400, 'The provided URL does not point to an MP3 file')

    # Full file path
    file_path = os.path.join(DOWNLOAD_FOLDER, mp3_filename)
    print(file_path)

    # Check if the file has already been downloaded
    if not os.path.isfile(file_path):
        # Send a GET request to download the MP3 file
        response = requests.get(mp3_url)
        print(response.status_code,mp3_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
        else:
            abort(response.status_code)  # Return the original error if the file can't be downloaded

    return file_path

@app.route('/downloads/<filename>.mp3')
def serve_mp3(filename):
    # Construct the full file path
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{filename}.mp3")

    # Check if the file exists
    if os.path.isfile(file_path):
        # If the file exists, send it
        return send_file(file_path, as_attachment=True)
    else:
        # If the file does not exist, return 404 Not Found
        abort(404, 'MP3 file not found')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8126)