if __name__ == '__main__':
    from pdf_to_txt_to_mp3 import Converter

    Converter.pdf_to_txt().convert_all()
    Converter.txt_to_mp3().convert_all()
