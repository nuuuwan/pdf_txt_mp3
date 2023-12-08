import os
import tempfile
from functools import cached_property

import requests
from gtts import gTTS
from pdfminer.high_level import extract_text
from pydub import AudioSegment
from utils import File, JSONFile, Log

log = Log('Converter')

DIR_DATA = 'data'


class Converter:
    def __init__(self, ext_source: str, ext_target: str, convert: callable):
        self.ext_source = ext_source
        self.ext_target = ext_target
        self.convert = convert

    @cached_property
    def dir_source(self) -> str:
        return os.path.join(DIR_DATA, self.ext_source)

    @cached_property
    def dir_target(self) -> str:
        return os.path.join(DIR_DATA, self.ext_target)

    def init_dirs(self):
        if not os.path.exists(self.dir_source):
            os.makedirs(self.dir_source)

        if not os.path.exists(self.dir_target):
            os.makedirs(self.dir_target)

    def process_filename(self, filename: str) -> bool:
        if not filename.endswith(self.ext_source):
            return False
        path_source = os.path.join(self.dir_source, filename)
        path_target = os.path.join(
            self.dir_target,
            filename[: -len(self.ext_source)] + self.ext_target,
        )

        if os.path.exists(path_target):
            log.warning(f'☑️ {path_target} already exists')
            return False

        if self.convert(path_source, path_target):
            return True
        return False

    def convert_all(self):
        self.init_dirs()
        n = 0
        for filename in os.listdir(self.dir_source):
            if self.process_filename(filename):
                n += 1

        log.info(f'✅✅ Converted {n} pdf files to txt files')

    @staticmethod
    def pdf_to_txt():
        def clean_line(line: str) -> str:
            n_alpha = len([c for c in line if c.isalpha()])
            if n_alpha < 10:
                return ''
            return line.strip()

        def clean_paragraph(paragraph: str) -> str:
            lines = paragraph.split('\n')
            lines = [clean_line(line) for line in lines]
            lines = [line for line in lines if line]
            return ' '.join(lines)

        def clean_text(text: str) -> str:
            paragraphs = text.split('\n\n')
            paragraphs = [
                clean_paragraph(paragraph) for paragraph in paragraphs
            ]
            paragraphs = [paragraph for paragraph in paragraphs if paragraph]
            return '\n\n'.join(paragraphs)

        def convert(path_source: str, path_target: str) -> bool:
            text = clean_text(extract_text(path_source))

            File(path_target).write(text)
            log.info(f'✅ Converted {path_source} to {path_target}')
            return True

        return Converter('pdf', 'txt', convert)

    @staticmethod
    def txt_to_mp3():
        def convert_paragraph(pararaph: str, i: int, n: int) -> str:
            temp_path = tempfile.mktemp(suffix='.mp3')
            tts = gTTS(pararaph, lang='en', tld='co.uk', slow=False)
            tts.save(temp_path)
            audio = AudioSegment.from_file(temp_path)
            log.debug(f'{i+1}/{n} -> {temp_path}')
            return audio

        def convert(path_source: str, path_target: str) -> bool:
            text = File(path_source).read()
            paragraphs = text.split('\n\n')
            combined_audio = AudioSegment.empty()
            n = len(paragraphs)
            for i, paragraph in enumerate(paragraphs):
                audio = convert_paragraph(paragraph, i, n)
                combined_audio += audio

            combined_audio.export(path_target, format='mp3')
            log.info(f'✅ Converted {path_source} to {path_target}')
            return True

        return Converter('txt', 'mp3', convert)

    @staticmethod
    def json_to_pdf():
        def process_data(data):
            url = data['url']
            basename = data['basename']

            path_target = os.path.join(DIR_DATA, 'pdf', basename + '.pdf')
            if os.path.exists(path_target):
                log.warning(f'☑️ {path_target} already exists')
                return

            # download binary from url using requests
            response = requests.get(url)
            with open(path_target, 'wb') as f:
                f.write(response.content)
            log.info(f'✅ Converted {url} to {path_target}')

        def convert(path_source: str, _) -> bool:
            data_list = JSONFile(path_source).read()
            for data in data_list:
                process_data(data)

        return Converter('json', 'pdf', convert)
