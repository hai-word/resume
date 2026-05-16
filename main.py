import json
import hashlib
from flask import Flask, request, jsonify
import redis
from pdf_parser import extract_pdf_text
from info_extractor import extract_basic_info, extract_background
from matcher import match_resume_jd
from flask_cors import CORS  # 跨域

# ✅ 只创建一次 app，并且配置 CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域（生效）

# Redis 缓存配置（本地自动关闭）
REDIS_CONFIG = {
    "host": "your-redis-host",
    "port": 6379,
    "password": "your-redis-password",
    "db": 0,
    "decode_responses": False
}

try:
    redis_client = redis.Redis(**REDIS_CONFIG)
    redis_client.ping()
    CACHE_ENABLED = True
except:
    CACHE_ENABLED = False  # ✅ 本地会自动关闭缓存

# 缓存工具
def get_cache_key(data):
    return hashlib.md5(json.dumps(data, ensure_ascii=False).encode()).hexdigest()

def get_from_cache(key):
    if not CACHE_ENABLED:
        return None
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_to_cache(key, data, expire=3600):
    if not CACHE_ENABLED:
        return
    redis_client.setex(key, expire, json.dumps(data, ensure_ascii=False))

# ==================== 接口 ====================
@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    try:
        # 获取上传文件
        if "file" not in request.files:
            return jsonify({"code": 400, "msg": "未上传文件", "data": None})

        file = request.files["file"]
        if not file.filename.endswith(".pdf"):
            return jsonify({"code": 400, "msg": "仅支持PDF文件", "data": None})

        # ✅ 修复：Windows 兼容临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            file.save(tmp_file.name)
            text = extract_pdf_text(tmp_file.name)

        return jsonify({
            "code": 200,
            "msg": "解析成功",
            "data": {
                "text": text,
                "length": len(text)
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": f"解析失败：{str(e)}", "data": None})


@app.route("/api/extract-info", methods=["POST"])
def extract_info():
    try:
        req = request.get_json()
        text = req.get("text", "")
        if not text:
            return jsonify({"code": 400, "msg": "文本不能为空", "data": None})

        key = get_cache_key({"type": "extract", "text": text})
        cache_data = get_from_cache(key)
        if cache_data:
            return jsonify({"code": 200, "msg": "success", "data": cache_data})

        basic = extract_basic_info(text)
        background = extract_background(text)
        result = {**basic, **background}
        set_to_cache(key, result)

        return jsonify({"code": 200, "msg": "success", "data": result})

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e), "data": None})

@app.route("/api/match-jd", methods=["POST"])
def match_jd():
    try:
        req = request.get_json()
        resume_text = req.get("resume_text", "")
        jd = req.get("jd", "")

        if not resume_text or not jd:
            return jsonify({"code": 400, "msg": "简历文本和岗位描述不能为空", "data": None})

        key = get_cache_key({"type": "match", "resume": resume_text, "jd": jd})
        cache_data = get_from_cache(key)
        if cache_data:
            return jsonify({"code": 200, "msg": "success", "data": cache_data})

        basic = extract_basic_info(resume_text)
        background = extract_background(text=resume_text)
        match = match_resume_jd(resume_text, jd)

        result = {
            "basic_info": basic,
            "background": background,
            "match_result": match
        }
        set_to_cache(key, result)

        return jsonify({"code": 200, "msg": "success", "data": result})

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e), "data": None})

# 阿里云入口
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
