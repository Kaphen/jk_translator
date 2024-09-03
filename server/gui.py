import os
from time import sleep

import pywebio
from pywebio import pin
from pywebio.output import *
import requests

from utils import LOG

ASSET_FOLDER = 'asset'  # 你可以根据需要更改此路径
os.makedirs(ASSET_FOLDER, exist_ok=True)  # 创建目录（如果不存在）


class GUI:

    def __init__(self):
        self.glm_model_url = None
        self.openai_model_name = None
        self.file_format = None
        self.model_type = None
        self.target_language = None
        self.uploaded_file = None

    def gui_index(self):
        pywebio.config(title='PDF多语言在线AI翻译器')
        # 添加 Logo
        put_markdown('# PDF多语言在线AI翻译器')
        put_html('<br>')
        pin.put_file_upload('uploaded_file', label='请上传一个PDF文件:', accept='application/pdf', placeholder='点击选择一个本地文件')
        pin.put_select('target_language', label='你想要翻译成什么语言:', options=['中文简体', '英语', '法语', '日语'])
        pin.put_select(name='model_type', label='请选择要使用的大语言模型:', options=['OpenAIModel', 'GLMModel'])
        put_scope('model_config')
        pin.put_select(name='file_format', label='请选择要输出文件的格式:', options=['markdown', 'pdf'])

        put_button('Submit', onclick=self.do_tasks_and_update_result)
        put_html('<br>')
        put_scope('loading')

        last_model_type = ''
        # openai和glm的配置相关组件随model_type展示
        while True:
            model_type = pin.pin['model_type']
            if last_model_type != model_type:
                with use_scope('model_config', clear=True):
                    if model_type == 'OpenAIModel':
                        pin.put_select('openai_model_name', label='请选择要使用的OpenAI模型:',
                                       options=['gpt-3.5-turbo', 'gpt-4o-turbo',
                                                'gpt-4o-mini'])
                    elif model_type == 'GLMModel':
                        pin.put_input('glm_model_url', label='请输入GLM模型的URL:', placeholder='http://xxx:xx')
                last_model_type = model_type
            sleep(1)


    def do_tasks_and_update_result(self):
        # 校验请求
        with use_scope('loading', clear=True):
            put_text('正在校验请求。。。。。。', scope='loading').style(
                'color: green; font-size: 20px')
            put_progressbar('bar')
            set_progressbar('bar', 5 / 100)
            err = self.check_parms()
            if err:
                clear('loading')
                put_text('校验请求失败，请检查上面的配置', scope='loading').style(
                    'color: red; font-size: 20px')
                return
        # 发送请求
        with use_scope('loading', clear=True):
            put_text('正在提交请求。。。。。。', scope='loading').style(
                'color: green; font-size: 20px'),
            put_progressbar('bar')
            set_progressbar('bar', 10 / 100)
            result, output_filename = self.send_http_request_triget_translate()
            print(f'回调函数被调用，接收到结果: statuscode={result}, 输出文件名={output_filename}')

        if result:
            # 请求成功则轮询任务执行结果
            with use_scope('loading', clear=True):
                put_text('正在进行文件解析和翻译，请耐心等待10秒至5分钟。。。。。。', scope='loading').style(
                    'color: green; font-size: 20px'),
                put_progressbar('bar')
                set_progressbar('bar', 20 / 100)
            self.polling_get_file(output_filename, 10, 20)
        else:
            # 请求失败则报错
            with use_scope('loading', clear=True):
                clear('loading')
                put_text('翻译请求失败，请联系管理员', scope='loading').style(
                    'color: red; font-size: 20px')


    def check_file(self):
        if self.uploaded_file:
            LOG.info('打开文件')
            open(f'{ASSET_FOLDER}/{self.uploaded_file["filename"]}', 'wb').write(self.uploaded_file['content'])
            return
        else:
            return '请传入文件!!'
            # return


    def check_parms(self):
        self.uploaded_file = pin.pin['uploaded_file']
        error = self.check_file()
        if error:
            toast(f'{error}', color='warn')
            return '请选择文件!!'

        self.target_language = pin.pin['target_language']
        self.model_type = pin.pin['model_type']
        self.file_format = pin.pin['file_format']
        if self.model_type == 'OpenAIModel':
            self.openai_model_name = pin.pin['openai_model_name']
        elif self.model_type == 'GLMModel':
            self.glm_model_url = pin.pin['glm_model_url']


    def polling_get_file(self, output_filename, times=30, init_progress=20):
        progress = init_progress
        while True:
            status_code, body = self.send_http_request_get_file(output_filename)
            if status_code != 200 and status_code != 404:
                clear('loading')
                put_text(f'轮询请求失败，请联系管理员\n{body}', scope='loading').style(
                    'color: red; font-size: 20px')
                break
            if status_code == 200 and body:
                with use_scope('loading', clear=True):
                    put_text('翻译完成！！！请点击下面的文件下载').style('color: green; font-size: 20px')
                    if self.file_format == 'pdf':
                        put_file(output_filename, body)
                    else:
                        put_file(output_filename, body)
                    break
            else:
                sleep(1)
                times -= 1
                progress = progress + 1 if progress < 99 else 99
                set_progressbar('bar', progress / 100)
                if times <= 0:
                    clear('loading')
                    put_text(f'文件解析或翻译超时，请联系管理员查看错误日志', scope='loading').style(
                        'color: red; font-size: 20px')
                    break

    def send_http_request_triget_translate(self):
        data = {
            'request_type': 'gui',
            'target_language': self.target_language,
            'model_type': self.model_type,
            'file_formal': self.file_format,
            'openai_model_name': self.openai_model_name,
            'glm_model_url': self.glm_model_url
        }
        url = 'http://127.0.0.1:8080/api/translate'
        files = {
            'file': (self.uploaded_file['filename'], self.uploaded_file['content']),  # 'file' 是表单字段的名称
        }
        LOG.info(f'准备发送请求{url}，data={data}')
        response = requests.post(url, files=files, data=data)
        LOG.info(f'translate返回rode={response.status_code},text={response.text},file={self.uploaded_file["filename"]}')
        if response.status_code == 200:
            return True, response.text
        else:
            return False, None

    def send_http_request_get_file(self, output_filename):
        sleep(2)
        url = f'http://127.0.0.1:8080/api/getFile/{output_filename}'
        LOG.info(f'准备发送请求{url}')
        response = requests.get(url)
        status_code = response.status_code
        LOG.info(f'getFile返回rode={status_code}')
        if response.status_code == 200:
            return status_code, response.content
        else:
            return status_code, response.text
