import re

def extract_basic_info(text):
    """提取必选字段：姓名、电话、邮箱、地址"""
    info = {
        "name": "",
        "phone": "",
        "email": "",
        "address": ""
    }

    lines = text.split("\n")

    # 1. 姓名 — 优先匹配"姓 名"前缀，再兜底纯中文行（排除性别行）
    name_match = re.search(r"姓\s*名\s*[:：]?\s*([一-龥]{2,4})", text)
    if name_match:
        info["name"] = name_match.group(1)
    else:
        for line in lines[:5]:
            line = line.strip()
            if re.fullmatch(r"^[一-龥]{2,4}$", line) and "性别" not in line:
                info["name"] = line
                break

    # 2. 手机号
    phone_match = re.search(r"1[3-9]\d{9}", text)
    if phone_match:
        info["phone"] = phone_match.group()

    # 3. 邮箱
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        info["email"] = email_match.group()

    # 4. 地址 — 匹配"地址"/"所在地"前缀或已知城市列表
    addr_label = re.search(r"(?:地址|所在地)\s*[:：]?\s*([^\n]{2,20})", text)
    if addr_label:
        info["address"] = addr_label.group(1).strip()
    else:
        cities = r"(?:北京|上海|广州|深圳|杭州|南京|武汉|成都|重庆|西安|郑州|长沙|苏州|天津|青岛|大连|厦门|宁波|合肥|福州|东莞|佛山|济南|沈阳|昆明|贵阳|南宁|海口|石家庄|太原|哈尔滨|长春|兰州|银川|西宁|拉萨|乌鲁木齐)(?:市|省)"
        addr_match = re.search(cities, text)
        if addr_match:
            info["address"] = addr_match.group()

    return info

def extract_background(text):
    """加分项：学历、工作年限、求职意向、项目经历"""
    data = {
        "education": "",
        "work_years": 0,
        "job_intention": "",
        "expected_salary": "",
        "projects": []
    }

    # 学历
    edu = re.search(r"(大专|本科|硕士|博士|研究生)", text)
    if edu:
        data["education"] = edu.group()

    # 工作年限
    year = re.search(r"(\d+)\s*年|工作\s*(\d+)", text)
    if year:
        data["work_years"] = int(year.group(1)) if year.group(1) else int(year.group(2))

    # 求职意向 — 冒号可选，适配"求职意向前端开发"和"求职意向：前端开发"
    job = re.search(r"求职意向\s*[:：]?\s*([^\n]{2,20})", text)
    if job:
        data["job_intention"] = job.group(1).strip()

    # 期望薪资
    salary = re.search(r"期望薪资\s*[:：]?\s*([^\n]+)", text)
    if salary:
        data["expected_salary"] = salary.group(1).strip()

    # 项目经历 — 匹配"项目经历"/"项目介绍"段落到下一个大标题或文末
    proj_match = re.search(r"(?:项目经历|项目介绍)\s*[:：]?\s*\n?(.+?)(?=\n\s*(?:教育|工作|技能|自我|证书|语言)|\Z)", text, re.DOTALL)
    if proj_match:
        proj_text = proj_match.group(1).strip()
        # 尝试按项目列表符号拆分
        items = re.split(r"\n(?=[•\-\d]+\.?\s*\S)", proj_text)
        if len(items) == 1:
            # 尝试按空行拆分
            items = re.split(r"\n\s*\n", proj_text)
        if len(items) == 1:
            # 按单行拆分（每行一个项目）
            items = proj_text.split("\n")
        data["projects"] = [p.strip() for p in items if len(p.strip()) > 10]

    return data
