from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def extract_keywords(text, top_k=15):
    """提取关键词"""
    stop_words = {"的", "和", "有", "在", "是", "可以", "能够", "相关", "负责", "进行", "熟悉", "掌握"}
    words = re.findall(r"[a-zA-Z]+|[\u4e00-\u9fa5]{2,}", text)
    words = [w for w in words if w not in stop_words and len(w) > 1]
    return list(set(words))[:top_k]

def calculate_similarity(a, b):
    """计算文本相似度"""
    try:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([a, b])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except:
        return 0.0

def match_resume_jd(resume_text, jd_text):
    """简历与JD匹配评分"""
    # 关键词匹配
    jd_kw = set(extract_keywords(jd_text))
    resume_kw = set(extract_keywords(resume_text))
    matched = jd_kw & resume_kw

    # 技能匹配率
    skill_rate = len(matched) / len(jd_kw) if jd_kw else 0.5

    # 文本相似度
    similarity = calculate_similarity(resume_text, jd_text)

    # 综合评分 0~100
    total_score = round((skill_rate * 0.6 + similarity * 0.4) * 100)

    return {
        "match_score": total_score,
        "skill_match_rate": round(skill_rate, 2),
        "similarity": round(similarity, 2),
        "matched_keywords": list(matched),
        "jd_keywords": list(jd_kw)
    }
