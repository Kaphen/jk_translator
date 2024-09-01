from gettext import translation
from typing import Optional

from book import ContentType
from model import Model
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG
import re

class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = '中文', output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)
        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                print(f'origin: {content.original}')
                # print(f'strip: {content.original.strip()}')
                # if content.original.strip() == '':
                #     print(f'不包含有效字符：{content.original}')
                #     continue
                # print(f'包含有效字符：{content.original}')

                prompt = self.model.translate_prompt(content, target_language)
                LOG.debug(prompt)
                # translation, status = self.model.make_request(prompt)
                # translation = content.original
                status = True
                translation = 'Test    Data\\nThis dataset contains two test samples provided by ChatGPT, an AI language model by OpenAI.\\nThese samples include a markdown table and an English text passage, which can be used to test an\nEnglish-to-Chinese translation software supporting both text and table formats.\nText  testing\nThe quick brown fox jumps over the lazy dog. This pangram contains every letter of the English\nalphabet at least once. Pangrams are often used to test fonts, keyboards, and other text-related\ntools. In addition to English, there are pangrams in many other languages. Some pangrams are more\ndifficult to construct due to the unique characteristics of the language.\nTable  Testing\nFruit                  Color            Price (USD)\nApple                  Red              1.20\nBanana                 Yellow           0.50\nOrange                 Orange           0.80\nStrawberry             Red              2.50\nBlueberry              Blue             3.00\nKiwi                   Green            1.00\nMango                  Orange           1.50\nGrape                  Purple           2.00'
                LOG.info(f'请求大模型结果：{translation}')


                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)
        output_file_path = self.writer.save_translated_book(self.book, output_file_path, file_format)
        return output_file_path


