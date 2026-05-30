#!/usr/bin/env python3
"""
Report Generator for SCI Paper Review System - 优化版
统一输出地道SCI学术英文，格式严格遵循需求
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_DB_FILE = "reviews.json"
DEFAULT_METADATA_FILE = "metadata.json"
DEFAULT_PARAMS_FILE = "params.json"
DEFAULT_OUTPUT_FILE = "review_report.txt"

# 期刊风格配置
JOURNAL_STYLES = {
    "nature": {"name": "Nature/Science", "opening": "To the Editor:"},
    "advanced_materials": {"name": "Advanced Materials/Wiley", "opening": "Dear Editor:"},
    "acs": {"name": "ACS", "opening": "Dear Editor:"},
    "ieee": {"name": "IEEE", "opening": "Dear Editor and Reviewers:"},
    "elsevier": {"name": "Elsevier", "opening": "Dear Editor,"},
    "springer": {"name": "Springer", "opening": "Dear Editor,"},
    "other": {"name": "General Scientific", "opening": "Dear Editors,"}
}


def load_data(
    db_path: str = DEFAULT_DB_FILE,
    metadata_path: str = DEFAULT_METADATA_FILE,
    params_path: str = DEFAULT_PARAMS_FILE
) -> Dict[str, Any]:
    """加载所有数据"""
    data = {"reviews": {}, "metadata": {}, "params": {}}
    
    if Path(db_path).exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            data["reviews"] = json.load(f)
    if Path(metadata_path).exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data["metadata"] = json.load(f)
    if Path(params_path).exists():
        with open(params_path, 'r', encoding='utf-8') as f:
            data["params"] = json.load(f)
    
    return data


def get_paper_vocabulary(metadata: Dict) -> Dict[str, List[str]]:
    """从论文中提取专业词汇用于复用"""
    abstract = metadata.get("abstract", "")
    title = metadata.get("title", "")
    keywords = metadata.get("keywords", [])
    
    # 提取关键术语
    terms = {
        "technical_terms": [],
        "methods": [],
        "materials": [],
        "properties": []
    }
    
    # 从摘要和关键词中提取
    text = abstract + " " + title + " " + " ".join(keywords)
    
    # 常见的专业术语模式
    term_patterns = {
        "methods": [r'\b(synthesis|preparation|fabrication|characterization|analysis)\b',
                   r'\b(dispersion|aggregation|crystallization|polymerization)\b'],
        "materials": [r'\b(nanoparticles|nanowires|nanostructure|composite|membrane)\b',
                     r'\b(polymer|graphene|carbon|metal|oxide)\b'],
        "properties": [r'\b(conductivity|thermal|stability|mechanical|optical)\b',
                      r'\b(efficiency|performance|sensitivity|selectivity)\b']
    }
    
    for category, patterns in term_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms[category].extend(matches)
    
    terms["technical_terms"] = list(set(keywords))
    
    return terms


def generate_opening_paragraph(metadata: Dict, params: Dict, comments: List[Dict]) -> str:
    """生成第一段：研究领域+核心成果+创新评价+现存问题+终审结论"""
    lines = []
    
    # 论文基本信息
    title = metadata.get("title", "This manuscript")
    authors_list = metadata.get("authors", [])
    author_str = ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")
    keywords = metadata.get("keywords", [])
    research_area = metadata.get("research_area", keywords[:3] if keywords else ["the field"])
    abstract = metadata.get("abstract", "")
    
    # 核心成果提取（从摘要中提取关键信息）
    core_findings = ""
    if abstract:
        # 提取摘要中的关键发现
        finding_patterns = [
            r'we\s+(show|demonstrate|report|find|present)',
            r'this\s+study\s+(reveals|shows|presents|reports)',
            r'(significantly|markedly|substantially)\s+\w+',
            r'(increased|decreased|improved|enhanced|reduced)\s+\w+'
        ]
        for pattern in finding_patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                # 提取该句
                start = max(0, match.start() - 20)
                end = min(len(abstract), match.end() + 80)
                sentence = abstract[start:end].strip()
                if len(sentence) > 20:
                    core_findings = sentence
                    break
    
    # 创新性评价
    novelty_level = params.get("novelty_level", "Not specified")
    novelty_map = {
        "Original": ("original contribution", "significantly advances"),
        "Incremental": ("incremental advance", "provides additional evidence for"),
        "Derivative": ("derivative work", "applies established methods to")
    }
    novelty_desc = novelty_map.get(novelty_level, ("contribution", "presents"))
    
    # 学术影响力
    impact_level = params.get("academic_impact", "Medium")
    impact_map = {
        "High": "significant scientific value and broad relevance to the research community",
        "Medium": "reasonable scientific value to the specialized community",
        "Low": "limited incremental scientific value"
    }
    impact_desc = impact_map.get(impact_level, "moderate scientific value")
    
    # 统计问题
    fatal = len([c for c in comments if c.get("severity") == "Fatal"])
    major = len([c for c in comments if c.get("severity") == "Major"])
    minor = len([c for c in comments if c.get("severity") == "Minor"])
    editorial = len([c for c in comments if c.get("severity") == "Editorial"])
    
    # 生成客观问题陈述
    issues_desc = []
    if fatal > 0:
        issues_desc.append(f"{fatal} critical issue(s)")
    if major > 0:
        issues_desc.append(f"{major} major concern(s)")
    if minor > 0:
        issues_desc.append(f"{minor} minor issue(s)")
    if editorial > 0:
        issues_desc.append(f"{editorial} editorial matter(s)")
    
    issues_summary = "; ".join(issues_desc) if issues_desc else "no major issues"
    
    # 终审结论
    reviewer_attitude = params.get("reviewer_attitude", "Constructive")
    
    if fatal > 0:
        recommendation = "Reject"
        recommendation_reason = "Critical issues must be resolved before reconsideration"
    elif major > 2:
        recommendation = "Major Revision"
        recommendation_reason = "Significant revisions are required to address major concerns"
    elif major > 0:
        recommendation = "Minor Revision"
        recommendation_reason = "Minor revisions are recommended to strengthen the manuscript"
    else:
        recommendation = "Accept"
        recommendation_reason = "The manuscript meets the standards for publication"
    
    # 组装第一段
    lines.append(f"The manuscript entitled \"{title}\" by {author_str} addresses research in {research_area[0] if research_area else 'the field'}. ")
    
    if core_findings:
        lines.append(f"This study {core_findings}. ")
    
    lines.append(f"The work represents an {novelty_desc[0]} that {novelty_desc[1]} current understanding in this area and demonstrates {impact_desc}. ")
    
    lines.append(f"The reviewers have identified {issues_summary} requiring attention. ")
    
    lines.append(f"Based on the comprehensive evaluation, this reviewer recommends {recommendation} ({recommendation_reason}).")
    
    return "".join(lines)


def format_detailed_comments(comments: List[Dict], ai_issues: List[Dict] = None) -> str:
    """格式化详细意见：逐条编号，无二级标题"""
    lines = []
    
    if not comments and not ai_issues:
        return "No formal comments submitted."
    
    # 合并所有意见
    all_items = []
    
    for c in comments:
        all_items.append({
            "id": c.get("comment_id", ""),
            "severity": c.get("severity", ""),
            "category": c.get("category", ""),
            "location": c.get("location", ""),
            "content": c.get("content", ""),
            "evidence": c.get("evidence", ""),
            "source": "Formal Review"
        })
    
    for i, issue in enumerate(ai_issues or [], 1):
        all_items.append({
            "id": f"AI_{i}",
            "severity": issue.get("severity", "Minor"),
            "category": issue.get("category", ""),
            "location": issue.get("location", ""),
            "content": issue.get("issue", issue.get("content", "")),
            "evidence": issue.get("example", ""),
            "source": "AI Objective Review",
            "ai_note": issue.get("note", "")
        })
    
    # 按严重性排序
    severity_order = {"Fatal": 0, "Major": 1, "Minor": 2, "Editorial": 3}
    all_items.sort(key=lambda x: severity_order.get(x["severity"], 3))
    
    # 逐条输出
    for i, item in enumerate(all_items, 1):
        # 编号 + 严重性 + 类别
        line_parts = [f"{i}."]
        if item["severity"]:
            line_parts.append(f"[{item['severity']}]")
        if item["category"]:
            line_parts.append(f"({item['category']})")
        if item["location"]:
            line_parts.append(f"- {item['location']}")
        
        lines.append(" ".join(line_parts))
        
        # 内容
        if item["content"]:
            lines.append(f"   {item['content']}")
        
        # 证据/示例
        if item.get("evidence"):
            lines.append(f"   Evidence: {item['evidence']}")
        
        # AI标注
        if item.get("source") == "AI Objective Review" and item.get("ai_note"):
            lines.append(f"   Note: {item['ai_note']}")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_ai_reference_section(ai_opinions: List[Dict]) -> str:
    """生成AI参考观点部分"""
    lines = []
    
    if not ai_opinions:
        return ""
    
    lines.append("\n" + "=" * 60)
    lines.append("AI REFERENCE COMMENTS")
    lines.append("[Only for expert personal reference, not valid for official review]")
    lines.append("=" * 60 + "\n")
    
    for i, opinion in enumerate(ai_opinions, 1):
        lines.append(f"{i}. [{opinion.get('category', 'General')}]")
        lines.append(f"   {opinion.get('opinion', '')}")
        lines.append(f"   Confidence: {opinion.get('confidence', 'Unknown')}")
        lines.append(f"   [AI reference comments, only for expert personal reference, not valid for official review]")
        lines.append("")
    
    return "\n".join(lines)


def generate_report(
    db_path: str = DEFAULT_DB_FILE,
    metadata_path: str = DEFAULT_METADATA_FILE,
    params_path: str = DEFAULT_PARAMS_FILE,
    journal_type: str = "other",
    ai_issues: List[Dict] = None,
    ai_opinions: List[Dict] = None,
    output_path: str = DEFAULT_OUTPUT_FILE
) -> Dict[str, Any]:
    """生成完整审稿报告"""
    data = load_data(db_path, metadata_path, params_path)
    
    reviews = data["reviews"]
    metadata = data["metadata"]
    params = data["params"]
    
    comments = reviews.get("comments", [])
    style_config = JOURNAL_STYLES.get(journal_type.lower(), JOURNAL_STYLES["other"])
    
    # 构建报告
    report_lines = []
    
    # Header
    report_lines.append("=" * 70)
    report_lines.append("SCI PEER REVIEW REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Review ID: {reviews.get('review_id', 'N/A')}")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    report_lines.append(f"Journal Style: {style_config['name']}")
    report_lines.append("")
    report_lines.append(style_config["opening"])
    report_lines.append("")
    
    # 第一段：综合评述
    report_lines.append(generate_opening_paragraph(metadata, params, comments))
    report_lines.append("")
    
    # 第二部分：详细意见
    report_lines.append("-" * 70)
    report_lines.append("DETAILED COMMENTS")
    report_lines.append("-" * 70)
    report_lines.append("")
    report_lines.append(format_detailed_comments(comments, ai_issues))
    
    # AI参考观点
    if ai_opinions:
        report_lines.append(generate_ai_reference_section(ai_opinions))
    
    # Footer
    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("END OF REVIEW REPORT")
    report_lines.append("=" * 70)
    
    report_content = "\n".join(report_lines)
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return {
        "success": True,
        "output_path": output_path,
        "journal_style": style_config["name"],
        "stats": {
            "total_comments": len(comments),
            "ai_issues": len(ai_issues) if ai_issues else 0,
            "formal_items": len(comments),
            "ai_reference_items": len(ai_opinions) if ai_opinions else 0
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate SCI Review Report")
    parser.add_argument("--input", "-i", default=DEFAULT_DB_FILE)
    parser.add_argument("--metadata", "-m", default=DEFAULT_METADATA_FILE)
    parser.add_argument("--params", "-p", default=DEFAULT_PARAMS_FILE)
    parser.add_argument("--journal", "-j", default="other",
                        choices=["nature", "advanced_materials", "ieee", "elsevier", "springer", "other"])
    parser.add_argument("--ai-issues", help="JSON file with AI detected issues")
    parser.add_argument("--ai-opinions", help="JSON file with AI reference opinions")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_FILE)
    
    args = parser.parse_args()
    
    ai_issues = None
    ai_opinions = None
    
    if args.ai_issues and Path(args.ai_issues).exists():
        with open(args.ai_issues, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ai_issues = data.get("hardcore_review_results", {})
            # 扁平化issues
            flat_issues = []
            for category, issues in ai_issues.items():
                if category != "ai_reference_opinions":
                    for issue in issues:
                        issue["category"] = category
                        flat_issues.append(issue)
            ai_issues = flat_issues
    
    if args.ai_opinions and Path(args.ai_opinions).exists():
        with open(args.ai_opinions, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ai_opinions = data.get("ai_reference_opinions", [])
    
    try:
        result = generate_report(
            db_path=args.input,
            metadata_path=args.metadata,
            params_path=args.params,
            journal_type=args.journal,
            ai_issues=ai_issues,
            ai_opinions=ai_opinions,
            output_path=args.output
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
