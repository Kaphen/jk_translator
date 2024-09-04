import os
import threading

from flask import request, jsonify, send_file, abort, Blueprint

from server.translate_task import Translate_Task
import asyncio

from utils import LOG

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


output_file_path = None
bp = Blueprint('main', __name__)

@bp.route('/api/probe', methods=['GET'])
async def probe():
    return jsonify({'msg': 'helloworld'}), 200

@bp.route('/api/translate', methods=['POST'])
def translate():
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
    if file_format == 'pdf':
        output_file_name = file.filename.replace('.pdf', f'_translated.pdf')
    else:
        output_file_name = file.filename.replace('.pdf', f'_translated.md')
    if os.path.isfile(f'{UPLOAD_FOLDER}/{output_file_name}'):
        os.remove(f'{UPLOAD_FOLDER}/{output_file_name}')
    thread = threading.Thread(target=task.async_run)
    thread.start()
    return output_file_name


# 翻译任务回调
def callback(future):
    global output_file_path
    try:
        output_file_path = future.result()
        LOG.info(f'任务执行成功，执行结果返回: {output_file_path}')
    except asyncio.CancelledError:
        LOG.error('回调中捕获到任务被取消')
    except Exception as e:
        LOG.error(f'Task raised an exception: {e}')


@bp.route('/api/getFile/<string:filename>', methods=['GET'])
def getFile(filename):
    jsonify({'message': f'获取文件: {filename}'})
    if filename:
        reference_file_path = f'{UPLOAD_FOLDER}/{filename}'
    else:
        reference_file_path = output_file_path
    absolute_file_path = f'{os.getcwd()}/{reference_file_path}'

    LOG.info(f'尝试获取文件{absolute_file_path}')
    try:
        if absolute_file_path:
            if not os.path.isfile(absolute_file_path):
                return jsonify({'error': '文件未找到', 'filepath': absolute_file_path}), 404
            return send_file(absolute_file_path, as_attachment=True)
        else:
            return jsonify({'error': '没有返回文件!'}), 404
    except FileNotFoundError as e:
        return jsonify({'error': '文件未找到', 'details': str(e)}), 404
    except Exception as e:
        return jsonify({'error': '发生错误', 'details': str(e)}), 500


