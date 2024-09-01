import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()

                # Store the original text content
                # raw_text = pdf_page.extract_text()
                # tables = pdf_page.extract_tables()
                # print(raw_text)
                # print(tables)
                raw_text = pdf_page.extract_text(layout=True)
                tables = pdf_page.extract_tables({
                    "text_layout": True,
                })
                print(raw_text)
                print(tables)

                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            raw_text = raw_text.replace(cell, "", 1)

                # Handling text
                if raw_text:
                    # Remove empty lines and leading/trailing whitespaces
                    raw_text_lines = raw_text.splitlines()
                    cleaned_raw_text_lines = [line.strip() for line in raw_text_lines if line.strip()]
                    cleaned_raw_text = "\\n".join(cleaned_raw_text_lines)

                    text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
                    page.add_content(text_content)
                    LOG.debug(f"[raw_text]\n {raw_text}")

                    # raw_text_lines = raw_text.splitlines()
                    # print(f"[raw_text_lines]\n {raw_text_lines}")
                    # new_text_list =[]
                    # for index, line in enumerate(raw_text_lines):
                    #     first_index, last_index = self.find_first_and_last_non_space(line)
                    #     if first_index > 0:
                    #         new_text_list.append(line[0:first_index-1])
                    #     new_text_list.append(line[first_index:last_index])
                    #     if last_index < len(line) - 1:
                    #         new_text_list.append(line[last_index+1:-1])
                    #     if index < len(raw_text_lines) - 1:
                    #         new_text_list.append('\n')
                    # print(f"[new_text_list: ]\n {new_text_list}")
                    # for new_content in new_text_list:
                    #     text_content = Content(content_type=ContentType.TEXT, original=new_content)
                    #     page.add_content(text_content)
                    # LOG.debug(f"[page.contents]\n {page.contents}")


                # Handling tables
                if tables:
                    table = TableContent(tables)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                book.add_page(page)

        return book

    def find_first_and_last_non_space(self, s):
        # 查找第一个非空格字符的位置
        first_non_space_index = next((i for i, char in enumerate(s) if char != ' '), 0)

        # 查找最后一个非空格字符的位置
        last_non_space_index = next((i for i, char in enumerate(reversed(s)) if char != ' '), -1)

        # 如果找到了最后一个非空格字符，计算其在原字符串中的索引
        if last_non_space_index is not None:
            last_non_space_index = len(s) - 1 - last_non_space_index

        return int(first_non_space_index), int(last_non_space_index)

p = PDFParser()
first_index, last_index = p.find_first_and_last_non_space(" line ")
print(f'第一个非空格索引为{first_index}，最后一个非空格索引为{last_index}')