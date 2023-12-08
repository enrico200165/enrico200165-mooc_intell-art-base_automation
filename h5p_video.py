
import os
import json
import shutil

from zipfile import ZipFile

from logdef_local import log

def zip_directory(directory_path, titolo, video_pathname, h5p_pathname):

    MODEL_PATH = r"D:\00_data\gdrive\enrico.viali_mirror\h5p_content\h5p_video_templ"
    if not os.path.isdir(MODEL_PATH):
        log.error(f"non esiste dir {MODEL_PATH}")
        exit(0)
    if not os.path.isdir(directory_path):
        log.error(f"non esiste dir {directory_path}")
        exit(0)
    if not os.path.isfile(video_pathname):
        log.error(f"non esiste video file {video_pathname}")
        exit(0)

    dest_video_file = None
    with ZipFile(h5p_pathname, 'w') as zipf:
        for root, dirs, files in os.walk(MODEL_PATH):
            for file in files:

                if file == "content.json":
                    pathname = os.path.join(root, file)
                    if not os.path.isfile(pathname):
                        log.error(f"non esiste video file {pathname}")
                        exit(0)

                    with open(pathname, "r") as content_json:
                        json_dict = json.load(content_json)
                    with open(pathname, "w") as content_json:
                        json_dict['interactiveVideo']['video']['startScreenOptions']['title'] = titolo
                        json_dict['interactiveVideo']['video']['startScreenOptions']['shortStartDescription'] = titolo
                        json_dict['interactiveVideo']['video']['files'][0]['path'] = os.path.join("videos",os.path.basename(video_pathname))
                        
                        copyright = json_dict['interactiveVideo']['video']['files'][0]["copyright"]
                        copyright['license'] = "Copyright © Scuola Futura https://scuolafutura.pubblica.istruzione.it"
                        copyright['title'] = titolo
                        copyright['author'] = "Enrico Viali - enrico.viali@gmail.com per Scuola Futura"
                        copyright["source"] = "Scuola Futura"
                        copyright["version"] = "1.0"

                        dest_video_file = os.path.join(MODEL_PATH, "content","videos",os.path.basename(video_pathname))
                        shutil.copy(video_pathname, dest_video_file)
                        json.dump(json_dict, content_json)

                if file == "h5p.json":
                    pathname = os.path.join(root, file)
                    if not os.path.isfile(pathname):
                        log.error(f"non esiste video file {pathname}")
                        exit(0)
                    with open(pathname, "r") as content_json:
                        json_dict = json.load(content_json)
                    json_dict['title'] = titolo
                    with open(pathname, "w") as content_json:
                        json.dump(json_dict, content_json)

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, MODEL_PATH)
                zipf.write(file_path, arcname=arcname)

    if dest_video_file is not None:
        os.remove(dest_video_file)
    else:
        log.error(f"{dest_video_file}")
    log.info(f"creato h5p package:\n{h5p_pathname} da:\n{video_pathname}")



if __name__ == "__main__":
    exit(0)
    # Specifica il percorso della directory da comprimere e il nome del file .zip
    directory_path = r"D:\00_data\gdrive\enrico.viali_mirror\h5p_content\interactive-video-prova-4"
    zip_filename = r"D:\00_data\gdrive\enrico.viali_mirror\h5p_content\prova.h5p"
    

    # Chiamata alla funzione per comprimere la directory
    zip_directory(directory_path, "titolo", "test_video.mp4", zip_filename)

    print(f"La directory '{directory_path}' è stata compressa in '{zip_filename}'.")
