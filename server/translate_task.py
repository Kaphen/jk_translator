import asyncio

from model import OpenAIModel
from translator import PDFTranslator
from utils import LOG


class Translate_Task:
    def __init__(self, request_type,  pdf_file_path, traget_language, mode_type, file_format,
                 openai_model_name, openai_api_key, glm_model_url, glm_timeout):
        self.output_file_path = None
        self.request_type = request_type
        self.traget_language = traget_language
        self.file_format = file_format
        self.pdf_file_path = pdf_file_path
        self.mode_type = mode_type
        if mode_type == 'OpenAIModel':
            self.model_name = openai_model_name
            self.api_key = openai_api_key
        elif mode_type == 'GLMModel':
            self.glm_mode_url = glm_model_url
            self.glm_timeout = glm_model_url


    async def async_run(self):
        LOG.info('开始执行翻译任务')
        model = OpenAIModel(model=self.model_name, api_key=self.api_key)
        translator = PDFTranslator(model)
        output_file_path = translator.translate_pdf(self.pdf_file_path, self.file_format, self.traget_language)
        LOG.info('翻译任务执行完成')
        return output_file_path


