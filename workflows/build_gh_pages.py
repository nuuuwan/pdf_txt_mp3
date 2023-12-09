import os

from utils import TIME_FORMAT_TIME, Log, Time, _

from pdf_to_txt_to_mp3 import Converter

RAW_DATA_URL_BASE = (
    'https://raw.githubusercontent.com/nuuuwan/pdf_txt_mp3/main'
)
INDEX_PATH = os.path.join(Converter.DIR_DATA, 'index.html')

log = Log('build_gh_pages')


def render_for_mp3(file_name_only: str, url: str):
    return _(
        'div',
        [
            _('h2', file_name_only),
            _(
                'audio',
                [
                    _('source', None, dict(src=url, type='audio/mpeg')),
                ],
                dict(controls='controls', style="width:90%; margin:6px;"),
            ),
        ],
    )


def render_for_ext(ext: str, file_name_only: str, url: str):
    if ext == 'mp3':
        return render_for_mp3(file_name_only, url)
    raise NotImplementedError(f'Unknown ext: {ext}')


def build_for_ext(ext: str):
    dir_ext = os.path.join(Converter.DIR_DATA, ext)
    child_list = []
    for file_name_only in os.listdir(dir_ext):
        file_path = os.path.join(dir_ext, file_name_only)
        url_file_path = file_path.replace('\\', '/')
        url = f'{RAW_DATA_URL_BASE}/{url_file_path}'

        child_list.append(render_for_ext(ext, file_name_only, url))

    head = _(
        'head',
        [
            _('title', 'PDF to TXT to MP3'),
        ],
    )
    time_str = TIME_FORMAT_TIME.stringify(Time.now())
    log.debug(f'{time_str=}')
    last_updated_text = f'Last Updated {time_str}.'
    body = _(
        'body',
        [
            _('h1', 'Contents'),
            _('p', last_updated_text),
            _('div', child_list),
        ],
    )
    html = _('html', [head, body])
    html.store(INDEX_PATH)
    log.info(f'Wrote {INDEX_PATH}')


if __name__ == '__main__':
    build_for_ext("mp3")
