#/usr/bin/env python3

# youtube2mp3.py v0.1 by Zaccareal
# requires ffmpeg binary 
# Usage: python3 youtube2mp3.py -u 'url'
# TODO: multiprocessing, speedup downloading

import argparse, requests, re, json, sys, subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', dest='urls', nargs='+', required=True)
    parser.add_argument('-nc','--no-conversion', dest='nc',  action='store_false')
    args = parser.parse_args()

    global s
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'})

    for url in args.urls:

        title, data = getJSON(url)
    
        #get max bitrate
        seq = [(data.index(x),x['bitrate']) for x in data if 'audio' in x['mimeType']] #list of tuples
        bit = max(seq,key=lambda item:item[1])[0] #max bitrate

        #get filename
        ext = re.search('audio/(.*); codecs=.*', data[bit]['mimeType'])
        filename = title+'.'+ext.group(1)
    
        print ('===================')
        print ('Title:',title)
        print ('Mime type:',data[bit]['mimeType'])
        print ('Audio quality:',data[bit]['audioQuality'])
        print ('Bitrate:', data[bit]['bitrate'])
        print ('Size: {0}MB'.format(round(int(data[bit]['contentLength'])/1024/1024, 1)))
        print ('Filename:', filename)
        print ('===================\n')

        download(data[bit]['url'], filename)

        if args.nc:
            convert(filename, title+'.mp3')

def getJSON(url):
    r = s.get(url)
    yt_json = re.search('ytplayer.config = (\{.+?\});', r.content.decode()) #json
    player_config = json.loads(yt_json.group(1))
    title = player_config['args']['title']
    player_response = json.loads(player_config['args']['player_response'])
    data = player_response['streamingData']['adaptiveFormats'] #list of dicts
    return title, data

def convert(file_input, file_output):
    print('Converting... -->', file_output)
    call = subprocess.call(['ffmpeg', '-i', file_input, '-codec:a', 'libmp3lame', '-b:a', '320k', file_output, '-v', '24'])

def download(url, filename):
    with open(filename, 'wb') as f:
        response = s.get(url, stream=True)
        total = response.headers.get('content-length')
        if total is None:
            print('Downloading...')
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=1024):
                downloaded += len(data)
                percentage = int(downloaded/total*100)
                f.write(data)
                sys.stdout.write('Downloading... {0}/{1} - {2}%'.format(downloaded, total, percentage))
                sys.stdout.write('\033[F')
                sys.stdout.flush()
                sys.stdout.write('\n')
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()
