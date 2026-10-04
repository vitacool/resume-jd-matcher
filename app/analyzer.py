import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List


TECH_KEYWORDS = {
    "python": ["python", "py"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "spring boot": ["spring boot", "springboot"],
    "mysql": ["mysql"],
    "sqlite": ["sqlite"],
    "redis": ["redis"],
    "mongodb": ["mongodb"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow"],
    "机器学习": ["机器学习", "machine learning", "ml"],
    "深度学习": ["深度学习", "deep learning"],
    "nlp": ["nlp", "自然语言处理"],
    "文本分类": ["文本分类", "text classification"],
    "embedding": ["embedding", "向量化", "词向量"],
    "rag": ["rag", "检索增强", "知识库问答"],
    "faiss": ["faiss"],
    "chroma": ["chroma", "chromadb"],
    "agent": ["agent", "智能体", "工具调用", "工具路由"],
    "llm": ["llm", "大模型", "openai", "deepseek", "通义", "智谱"],
    "api": ["api", "接口", "restful", "rest api"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "vue": ["vue"],
    "react": ["react"],
    "git": ["git", "github"],
    "linux": ["linux"],
    "docker": ["docker"],
    "数据结构": ["数据结构", "算法"],
    "后端开发": ["后端", "后端开发", "服务端"],
    "前端开发": ["前端", "前端开发", "页面"],
    "数据库": ["数据库", "db", "sqlite", "mysql", "redis", "mongodb"],
    "模型评估": ["模型评估", "precision", "recall", "f1", "准确率", "混淆矩阵"],
    "用户反馈": ["用户反馈", "人工纠错", "反馈闭环", "数据闭环"],
}

SOFT_KEYWORDS = {
    "学习能力": ["学习能力", "自学", "快速学习"],
    "项目落地": ["项目落地", "独立完成", "从0到1", "闭环"],
    "沟通协作": ["沟通", "协作", "团队"],
    "问题分析": ["问题分析", "定位问题", "优化"],
}

ROLE_KEYWORDS = {
    "ai应用开发": ["ai应用", "ai 应用", "ai开发", "大模型应用", "rag", "agent"],
    "ai agent": ["agent", "智能体", "工具调用", "工具路由"],
    "后端实习": ["后端", "fastapi", "接口", "数据库"],
    "算法基础": ["算法", "数据结构", "机器学习", "pytorch"],
}


@dataclass
class MatchResult:
    score: int
    level: str
    similarity: float
    resume_keywords: List[str]
    jd_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    suggestions: List[str]
    route: Dict[str, str]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def contains_any(text: str, variants: List[str]) -> bool:
    return any(variant.lower() in text for variant in variants)


def extract_keywords(text: str) -> List[str]:
    normalized = normalize_text(text)
    found = []
    for keyword, variants in {**TECH_KEYWORDS, **SOFT_KEYWORDS, **ROLE_KEYWORDS}.items():
        if contains_any(normalized, variants):
            found.append(keyword)
    return sorted(set(found))


def tokenize(text: str) -> List[str]:
    normalized = normalize_text(text)
    english_terms = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", normalized)
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
    chars = [token[i : i + 2] for token in chinese_terms for i in range(max(len(token) - 1, 0))]
    keywords = extract_keywords(text)
    return english_terms + chars + keywords


def vectorize(tokens: List[str]) -> Counter:
    return Counter(tokens)


def cosine_similarity(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    keys = set(left) | set(right)
    dot = sum(left[key] * right[key] for key in keys)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def classify_route(jd_keywords: List[str], missing_keywords: List[str]) -> Dict[str, str]:
    if "ai agent" in jd_keywords or "agent" in jd_keywords:
        return {
            "target_role": "AI Agent / AI 应用开发",
            "focus": "突出 RAG、工具路由、FastAPI 接口、知识库管理和反馈闭环。",
        }
    if "文本分类" in jd_keywords or "pytorch" in jd_keywords or "机器学习" in jd_keywords:
        return {
            "target_role": "机器学习 / NLP 应用开发",
            "focus": "突出 PyTorch 训练、模型评估、分类接口和数据集构建。",
        }
    if "后端开发" in jd_keywords or "api" in jd_keywords:
        return {
            "target_role": "后端 / AI 工程化开发",
            "focus": "突出 FastAPI、数据库设计、接口文档、日志记录和系统可维护性。",
        }
    if missing_keywords:
        return {
            "target_role": "综合软件开发实习",
            "focus": f"优先补强 {missing_keywords[0]}，并用项目经历证明落地能力。",
        }
    return {
        "target_role": "AI 应用开发实习",
        "focus": "突出项目闭环、技术栈匹配度和可上线维护的工程能力。",
    }


def build_strengths(matched_keywords: List[str]) -> List[str]:
    strengths = []
    if {"python", "fastapi", "api"} & set(matched_keywords):
        strengths.append("具备 Python 后端接口开发基础，能够把 AI 能力封装成 Web API。")
    if {"pytorch", "文本分类", "模型评估"} & set(matched_keywords):
        strengths.append("有模型训练、文本分类和评估指标展示经验，适合 NLP 应用类岗位。")
    if {"rag", "embedding", "agent"} & set(matched_keywords):
        strengths.append("项目经历覆盖 RAG、Embedding 和 Agent 工具路由，和 AI 应用开发方向匹配。")
    if {"sqlite", "数据库", "用户反馈"} & set(matched_keywords):
        strengths.append("有 SQLite 记录、后台管理、用户纠错等数据闭环设计意识。")
    if not strengths:
        strengths.append("简历和岗位存在一定基础匹配，可以进一步补充项目细节提升说服力。")
    return strengths


def build_suggestions(missing_keywords: List[str], matched_keywords: List[str]) -> List[str]:
    suggestions = []
    priority = missing_keywords[:5]
    if priority:
        suggestions.append("在技术能力或项目经历中补充岗位高频关键词：" + "、".join(priority) + "。")
    if "模型评估" not in matched_keywords:
        suggestions.append("如果岗位偏算法或 NLP，建议写清楚准确率、Precision、Recall、F1 等模型评估结果。")
    if "api" not in matched_keywords and "fastapi" not in matched_keywords:
        suggestions.append("如果岗位偏应用开发，建议强调 API 设计、前后端联调和接口返回格式。")
    if "用户反馈" not in matched_keywords:
        suggestions.append("建议补充日志记录、用户纠错、样本回流等可维护系统设计，区别于普通 Demo。")
    suggestions.append("项目描述尽量使用“问题-方案-结果”的结构，并保留 GitHub 链接方便面试官查看代码。")
    return suggestions[:5]


def analyze_resume_jd(resume_text: str, jd_text: str) -> MatchResult:
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    matched_keywords = sorted(set(resume_keywords) & set(jd_keywords))
    missing_keywords = sorted(set(jd_keywords) - set(resume_keywords))

    resume_vec = vectorize(tokenize(resume_text))
    jd_vec = vectorize(tokenize(jd_text))
    similarity = cosine_similarity(resume_vec, jd_vec)

    keyword_recall = len(matched_keywords) / max(len(jd_keywords), 1)
    score = round(similarity * 45 + keyword_recall * 55)
    score = max(0, min(score, 100))

    if score >= 80:
        level = "高度匹配"
    elif score >= 60:
        level = "较匹配"
    elif score >= 40:
        level = "部分匹配"
    else:
        level = "匹配度偏低"

    return MatchResult(
        score=score,
        level=level,
        similarity=round(similarity, 4),
        resume_keywords=resume_keywords,
        jd_keywords=jd_keywords,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        strengths=build_strengths(matched_keywords),
        suggestions=build_suggestions(missing_keywords, matched_keywords),
        route=classify_route(jd_keywords, missing_keywords),
    )
