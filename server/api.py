import os

from flask import Flask, request, jsonify, send_file
from server.translate_task import Translate_Task
import asyncio

from utils import LOG

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


output_file_path = None
app = Flask(__name__)


@app.route('/api/translate', methods=['POST'])
async def translate():
    # 获取参数
    request_type = request.form.get('request_type', 'api')
    target_language = request.form.get('target_language', 'en')
    model_type = request.form.get('model_type', 'OpenAIModel')
    file_format = request.form.get('file_format', 'pdf')
    openai_model_name = request.form.get('openai_model_name', 'gpt-3.5-turbo')
    glm_model_url = request.form.get('glm_model_url', '')
    LOG.info(f'接收到请求： request_type={request_type}, target_language={target_language}')

    # 检验请求中的文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 保存文件
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # 触发翻译任务
    task = Translate_Task(request_type, file_path, target_language, model_type, file_format,
                          openai_model_name, None, glm_model_url, 300)
    async_task = asyncio.create_task(task.async_run())
    async_task.add_done_callback(callback)
    return '触发翻译成功'


# 翻译任务回调
def callback(future):
    global  output_file_path
    output_file_path = future.result()
    LOG.info(f'任务执行成功，执行结果返回: {output_file_path}')


@app.route('/api/getFile', methods=['GET'])
def getFile():
    LOG.info(f'output_file_path={output_file_path}')
    if output_file_path:
        return send_file(output_file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found!'}), 400

