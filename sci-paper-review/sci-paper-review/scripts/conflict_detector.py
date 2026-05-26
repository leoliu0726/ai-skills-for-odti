#!/usr/bin/env python3
"""
Conflict Detector for SCI Paper Review System - 增强版
检测审稿意见中的前后矛盾、重复、创新性评价冲突
全面客观硬核审查：逻辑矛盾、数据自洽性、图表规范、引文规范、实验信息缺失
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Any, List, Tuple

DEFAULT_DB_FILE = "reviews.json"
DEFAULT_METADATA_FILE = "metadata.json"
DEFAULT_OUTPUT_FILE = "conflicts.json"


def load_database(db_path: str = DEFAULT_DB_FILE) -> Dict[str, Any]:
    """加载审稿数据库"""
    if not db_path:
        db_path = DEFAULT_DB_FILE
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_metadata(metadata_path: str = DEFAULT_METADATA_FILE) -> Dict[str, Any]:
    """加载元数据"""
    if Path(metadata_path).exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两段文本的相似度"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def load_pdf_text(pdf_path: str, max_pages: int = 50) -> str:
    """加载PDF文本用于核查"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        
        # 智能采样：封面+均匀分布
        if len(doc) <= max_pages:
            page_indices = list(range(len(doc)))
        else:
            step = len(doc) // max_pages
            page_indices = list(range(0, len(doc), step))[:max_pages]
        
        full_text = ""
        for idx in page_indices:
            full_text += doc[idx].get_text() + f"\n[Page {idx + 1}]\n"
        
        doc.close()
        return full_text
    except Exception as e:
        return f"[PDF loading error: {e}]"


# ============================================================
# 硬核审查模块
# ============================================================

class HardcoreReviewer:
    """AI客观硬核审查器"""
    
    def __init__(self, pdf_path: str, metadata: Dict, comments: List[Dict]):
        self.pdf_path = pdf_path
        self.metadata = metadata
        self.comments = comments
        self.pdf_text = ""
        self.review_results = {
            "logic_conflicts": [],
            "data_consistency": [],
            "figure_table_issues": [],
            "citation_issues": [],
            "experiment_info_gaps": [],
            "language_issues": [],
            "ai_reference_opinions": []
        }
    
    def load_pdf(self):
        """加载PDF文本"""
        self.pdf_text = load_pdf_text(self.pdf_path)
        return self
    
    def check_logic_consistency(self) -> List[Dict]:
        """核查逻辑一致性"""
        issues = []
        
        # 检查摘要与方法的一致性
        abstract = self.metadata.get("abstract", "")
        if not abstract:
            return issues
        
        # 提取摘要中的关键声明
        claim_patterns = [
            r'(?:we show|we demonstrate|we report|our results|findings)',
            r'(\d+(?:\.\d+)?(?:\s*(?:fold|times|%|percent|mg|g|kg|ml|μL|mM|nM))+)',
            r'(increased|decreased|improved|reduced|enhanced|significantly)',
        ]
        
        # 检查数据引用一致性（数字、单位、百分比）
        number_refs = re.findall(r'(\d+(?:\.\d+)?)\s*(%|percent|fold|times)', self.pdf_text)
        if len(set(number_refs)) < len(number_refs) * 0.3:
            issues.append({
                "type": "logic_conflict",
                "category": "Logic Consistency",
                "severity": "Major",
                "issue": "某些数值在论文不同位置出现但含义可能不同",
                "ai_reference": True,
                "note": "[Uncertain] 需要人工核实具体数值的一致性"
            })
        
        # 检查方法与结论的逻辑链
        method_keywords = ["method", "approach", "technique", "procedure", "experiment"]
        conclusion_keywords = ["conclude", "conclusion", "therefore", "thus", "hence"]
        
        method_count = sum(1 for kw in method_keywords if kw.lower() in self.pdf_text[:5000].lower())
        conclusion_count = sum(1 for kw in conclusion_keywords if kw.lower() in self.pdf_text[-3000:].lower())
        
        if method_count == 0:
            issues.append({
                "type": "logic_conflict",
                "category": "Logic Consistency",
                "severity": "Minor",
                "issue": "方法部分可能缺失或位置异常",
                "ai_reference": True,
                "note": "建议人工确认方法章节存在"
            })
        
        self.review_results["logic_conflicts"] = issues
        return issues
    
    def check_data_consistency(self) -> List[Dict]:
        """核查数据自洽性"""
        issues = []
        
        # 检查数字格式一致性
        decimal_patterns = [
            r'\d+\.\d+',  # 1.23
            r'\d+,\d+',   # 1,23 (欧洲格式)
        ]
        
        # 提取所有带小数的数字
        decimals = re.findall(r'\d+[.,]\d+', self.pdf_text)
        
        # 检查是否有混用
        has_dot = any('.' in d for d in decimals[:100])
        has_comma = any(',' in d for d in decimals[:100])
        
        if has_dot and has_comma:
            issues.append({
                "type": "data_consistency",
                "category": "Data Consistency",
                "severity": "Minor",
                "issue": "数字格式混用（点号和逗号）",
                "ai_reference": True,
                "note": "建议核实小数点使用的一致性"
            })
        
        # 检查百分比格式
        percent_formats = [
            r'\d+(?:\.\d+)?%',
            r'\d+(?:\.\d+)?\s*percent',
            r'\d+(?:\.\d+)?\s*per\s*cent'
        ]
        
        for fmt in percent_formats:
            if re.search(fmt, self.pdf_text):
                issues.append({
                    "type": "data_consistency",
                    "category": "Data Consistency",
                    "severity": "Editorial",
                    "issue": "百分比表达格式不统一",
                    "ai_reference": True,
                    "note": "建议统一使用一种百分比格式"
                })
                break
        
        self.review_results["data_consistency"] = issues
        return issues
    
    def check_figure_table_format(self) -> List[Dict]:
        """核查图表规范"""
        issues = []
        
        # 检查Figure引用格式
        figure_patterns = [
            r'[Ff]igure\s+\d+[a-z]?',
            r'[Ff]ig\.\s*\d+[a-z]?',
            r'[Ff]ig\s+\d+[a-z]?',
        ]
        
        all_figure_refs = []
        for pattern in figure_patterns:
            all_figure_refs.extend(re.findall(pattern, self.pdf_text))
        
        # 检查引用格式一致性
        fig_refs = [r for r in all_figure_refs if 'Fig' in r and '.' in r]
        figure_refs = [r for r in all_figure_refs if 'Figure' in r]
        
        if fig_refs and figure_refs:
            issues.append({
                "type": "figure_table",
                "category": "Figure & Table Format",
                "severity": "Editorial",
                "issue": "Figure引用格式不一致（Fig./Figure混用）",
                "example": f"Found: {fig_refs[0] if fig_refs else ''}, {figure_refs[0] if figure_refs else ''}",
                "ai_reference": True,
                "note": "建议统一使用一种Figure引用格式"
            })
        
        # 检查Table引用格式
        table_patterns = [
            r'[Tt]able\s+\d+',
            r'[Tt]ab\.\s*\d+',
        ]
        
        all_table_refs = []
        for pattern in table_patterns:
            all_table_refs.extend(re.findall(pattern, self.pdf_text))
        
        if all_table_refs:
            tab_refs = [r for r in all_table_refs if 'Tab.' in r or 'tab.' in r]
            table_refs = [r for r in all_table_refs if 'Table' in r]
            
            if tab_refs and table_refs:
                issues.append({
                    "type": "figure_table",
                    "category": "Figure & Table Format",
                    "severity": "Editorial",
                    "issue": "Table引用格式不一致（Tab./Table混用）",
                    "ai_reference": True,
                    "note": "建议统一使用一种Table引用格式"
                })
        
        self.review_results["figure_table_issues"] = issues
        return issues
    
    def check_citation_format(self) -> List[Dict]:
        """核查引文规范"""
        issues = []
        
        # 检查常见的引用格式
        citation_patterns = [
            r'\[\d+\]',           # [1]
            r'\[\d+,\s*\d+\]',   # [1, 2]
            r'\[\d+\-\d+\]',     # [1-3]
            r'\(\w+,\s*\d{4}\)',  # (Author, 2020)
        ]
        
        citation_counts = {}
        for i, pattern in enumerate(citation_patterns):
            count = len(re.findall(pattern, self.pdf_text))
            if count > 0:
                citation_counts[f"format_{i+1}"] = {
                    "pattern": pattern,
                    "count": count,
                    "example": re.findall(pattern, self.pdf_text)[:3]
                }
        
        # 检测格式混用
        if len(citation_counts) > 1:
            formats = list(citation_counts.keys())
            issues.append({
                "type": "citation",
                "category": "Citation Format",
                "severity": "Minor",
                "issue": "参考文献引用格式不一致",
                "details": citation_counts,
                "ai_reference": True,
                "note": "建议统一使用一种引用格式"
            })
        
        self.review_results["citation_issues"] = issues
        return issues
    
    def check_experiment_info_gaps(self) -> List[Dict]:
        """核查实验信息缺失"""
        issues = []
        
        # 检查必要的实验信息
        required_info = {
            "sample_size": [r'\bn\s*=\s*\d+', r'sample.*\d+', r'n\s*\d+'],
            "replicates": [r'replicate', r'repeated\s*\d+\s*times', r'triplicate'],
            "statistical_test": [r't-test', r'ANOVA', r'p\s*value', r'mean\s*±\s*SD', r'mann-whitney'],
            "controls": [r'control', r'baseline', r'reference'],
        }
        
        found_info = {}
        for info_type, patterns in required_info.items():
            for pattern in patterns:
                if re.search(pattern, self.pdf_text, re.IGNORECASE):
                    found_info[info_type] = True
                    break
        
        missing_info = []
        for info_type in required_info:
            if info_type not in found_info:
                missing_info.append(info_type)
        
        if missing_info:
            issues.append({
                "type": "experiment_gap",
                "category": "Experiment Information",
                "severity": "Major" if len(missing_info) >= 2 else "Minor",
                "issue": f"部分实验必要信息可能缺失: {', '.join(missing_info)}",
                "ai_reference": True,
                "note": "[Uncertain] 需要人工核实实验方法描述的完整性"
            })
        
        self.review_results["experiment_info_gaps"] = issues
        return issues
    
    def check_language_quality(self) -> List[Dict]:
        """核查语言问题"""
        issues = []
        
        # 检查常见语病
        language_patterns = {
            "article_issues": [
                (r'\ba\s+[aeiouAEIOU]', "元音前应使用'an'"),
                (r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]', "辅音前应使用'a'"),
            ],
            "tense_issues": [
                (r'showed.*will|show.*will|found.*will', "时态可能不一致"),
            ],
            "plural_issues": [
                (r'data\s+is|data\s+was(?!n)', "data是复数名词"),
                (r'research\s+is(?!n)', "research可用作不可数"),
            ]
        }
        
        for category, patterns in language_patterns.items():
            for pattern, suggestion in patterns:
                if re.search(pattern, self.pdf_text):
                    issues.append({
                        "type": "language",
                        "category": "Language Quality",
                        "severity": "Editorial",
                        "issue": f"可能存在语言问题: {suggestion}",
                        "ai_reference": True,
                        "note": "建议人工核实语言表达"
                    })
                    break  # 每类只报告一次
        
        self.review_results["language_issues"] = issues
        return issues
    
    def generate_ai_reference_opinions(self) -> List[Dict]:
        """生成AI专业性参考观点（仅供专家参考，不作为正式评审）"""
        opinions = []
        
        abstract = self.metadata.get("abstract", "")
        title = self.metadata.get("title", "")
        keywords = self.metadata.get("keywords", [])
        text_to_check = (title + " " + abstract + " " + " ".join(keywords)).lower()
        
        # 1. 创新性评价
        novelty_indicators = {
            "high_novelty": ["novel", "first", "unprecedented", "new strategy", "breakthrough", "paradigm"],
            "moderate_novelty": ["improve", "enhance", "advance", "develop", "optimize", "modify"],
            "low_novelty": ["similar", "consistent with", "according to", "based on", "comparable"]
        }
        
        high_count = sum(1 for kw in novelty_indicators["high_novelty"] if kw in text_to_check)
        moderate_count = sum(1 for kw in novelty_indicators["moderate_novelty"] if kw in text_to_check)
        
        if high_count > moderate_count and high_count >= 2:
            novelty_assessment = "论文声称具有显著创新性，使用了'novel'/'first'/'breakthrough'等词汇。"
        elif moderate_count > high_count:
            novelty_assessment = "论文定位为改进性工作，使用了'enhance'/'improve'/'develop'等表述。"
        else:
            novelty_assessment = "从摘要和关键词来看，论文的创新性定位不够明确。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "创新性评价",
            "opinion": novelty_assessment,
            "confidence": "Low",
            "evidence": f"关键词: {', '.join(keywords[:5])}" if keywords else "",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 2. 是否突破领域瓶颈
        bottleneck_keywords = ["challenge", "bottleneck", "limit", "barrier", "obstacle", "critical issue"]
        breakthrough_keywords = ["overcome", "solve", "break through", "resolve", "surmount"]
        
        bottleneck_count = sum(1 for kw in bottleneck_keywords if kw in text_to_check)
        breakthrough_count = sum(1 for kw in breakthrough_keywords if kw in text_to_check)
        
        if bottleneck_count >= 2 and breakthrough_count >= 1:
            bottleneck_assessment = "论文明确指出领域瓶颈并声称已解决。"
        elif bottleneck_count >= 2:
            bottleneck_assessment = "论文识别了领域瓶颈，但解决路径的明确性待评估。"
        else:
            bottleneck_assessment = "论文未明确指出或解决领域瓶颈问题。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "领域瓶颈突破",
            "opinion": bottleneck_assessment,
            "confidence": "Low-Medium",
            "evidence": f"瓶颈词出现{bottleneck_count}次，解决词出现{breakthrough_count}次" if bottleneck_count else "",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 3. 研究重要性
        impact_keywords = {
            "strong": ["significant", "important", "crucial", "essential", "fundamental", "transformative"],
            "moderate": ["relevant", "meaningful", "valuable", "notable", "substantial"]
        }
        
        strong_impact = sum(1 for kw in impact_keywords["strong"] if kw in abstract.lower())
        moderate_impact = sum(1 for kw in impact_keywords["moderate"] if kw in abstract.lower())
        
        if strong_impact >= 2:
            impact_assessment = "论文使用强效价词汇强调研究重要性（significant/crucial/fundamental）。"
        elif strong_impact >= 1 or moderate_impact >= 2:
            impact_assessment = "论文适度强调了研究的重要性。"
        else:
            impact_assessment = "论文对研究重要性的阐述较为平淡。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "研究重要性",
            "opinion": impact_assessment,
            "confidence": "Medium",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 4. 学术路线价值
        methodology_keywords = ["method", "approach", "strategy", "protocol", "synthesis", "preparation"]
        methodology_count = sum(1 for kw in methodology_keywords if kw in abstract.lower())
        
        if methodology_count >= 2:
            route_assessment = "论文提出或优化了方法/路线，具有一定的学术路线价值。"
        elif methodology_count >= 1:
            route_assessment = "论文涉及方法学内容，学术路线价值待深入评估。"
        else:
            route_assessment = "论文侧重于结果描述，方法学路线价值不够突出。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "学术路线价值",
            "opinion": route_assessment,
            "confidence": "Medium",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 5. 数据深层真伪（基于一致性推断）
        # 检查数据引用的一致性
        number_pattern = r'\d+(?:\.\d+)?(?:\s*(?:fold|times|%))?'
        all_numbers = re.findall(number_pattern, abstract)
        unique_numbers = set(all_numbers)
        
        if len(all_numbers) > 3 and len(unique_numbers) == len(all_numbers):
            data_assessment = "摘要中的数值数据相互独立，未检测到明显矛盾。"
        elif len(all_numbers) > 3:
            data_assessment = "摘要中部分数值可能存在重复引用，请核实一致性。"
        else:
            data_assessment = "摘要中数据引用较少，深层真伪难以从文本推断。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "数据深层真伪",
            "opinion": data_assessment,
            "confidence": "Low",
            "evidence": f"摘要中发现{len(all_numbers)}个数值数据" if all_numbers else "",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 6. 复杂理论机理的自洽性
        theory_keywords = ["mechanism", "theory", "principle", "model", "simulation", "calculation"]
        theory_count = sum(1 for kw in theory_keywords if kw in abstract.lower())
        
        conclusion_text = self.metadata.get("conclusion", "")[:500] if self.metadata.get("conclusion") else ""
        theory_in_conclusion = sum(1 for kw in theory_keywords if kw in conclusion_text.lower())
        
        if theory_count >= 2 and theory_in_conclusion >= 1:
            theory_assessment = "论文涉及理论/机理分析，机理阐述与结论的一致性待核实。"
        elif theory_count >= 2:
            theory_assessment = "论文包含理论/机理内容，建议核实与结论的自洽性。"
        else:
            theory_assessment = "论文以实验研究为主，理论机理部分较弱。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "理论机理自洽性",
            "opinion": theory_assessment,
            "confidence": "Medium",
            "evidence": f"摘要理论词出现{theory_count}次" if theory_count else "",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        # 7. 期刊匹配度（基于研究领域和风格推断）
        journal = self.metadata.get("journal", "")
        
        if any(x in journal.lower() for x in ["nature", "science", "cell"]):
            journal_assessment = "期刊风格偏向综合性顶刊，对创新性和影响力要求较高。"
        elif any(x in journal.lower() for x in ["advanced", "angewandte", "wiley"]):
            journal_assessment = "期刊为高水平专业期刊，强调技术深度和创新性。"
        elif any(x in journal.lower() for x in ["acs", "jacs", "nano"]):
            journal_assessment = "ACS系列期刊注重化学/材料领域的技术严谨性。"
        elif "ieee" in journal.lower():
            journal_assessment = "IEEE期刊注重工程应用和技术实用性。"
        elif "springer" in journal.lower() or "elsevier" in journal.lower():
            journal_assessment = "期刊为综合性学术出版，对研究规范有明确要求。"
        else:
            journal_assessment = "期刊定位需根据期刊名称进一步判断。"
        
        opinions.append({
            "type": "ai_reference",
            "category": "期刊专业性评判标准匹配度",
            "opinion": journal_assessment,
            "confidence": "High",
            "evidence": f"识别期刊: {journal}" if journal else "",
            "disclaimer": "[AI reference comments, only for expert personal reference, not valid for official review]",
            "ai_reference": True
        })
        
        self.review_results["ai_reference_opinions"] = opinions
        return opinions
    
    def run_full_review(self) -> Dict[str, Any]:
        """执行全面审查"""
        self.load_pdf()
        
        self.check_logic_consistency()
        self.check_data_consistency()
        self.check_figure_table_format()
        self.check_citation_format()
        self.check_experiment_info_gaps()
        self.check_language_quality()
        self.generate_ai_reference_opinions()
        
        return self.review_results
    
    def format_review_results(self) -> str:
        """格式化审查结果供展示 - 分两部分"""
        lines = []
        
        # 第一部分：AI客观核查结果（格式规范性核查）
        all_issues = []
        for category, issues in self.review_results.items():
            if category == "ai_reference_opinions":
                continue
            for issue in issues:
                issue["_category"] = category
                all_issues.append(issue)
        
        # 按严重性排序
        severity_order = {"Fatal": 0, "Major": 1, "Minor": 2, "Editorial": 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "Minor"), 3))
        
        lines.append("=" * 70)
        lines.append("第一部分：AI客观核查结果")
        lines.append("(格式规范性核查 - 只客观陈述事实)")
        lines.append("=" * 70)
        lines.append("")
        
        if not all_issues:
            lines.append("未检测到明显的格式规范性问题。")
        else:
            for i, issue in enumerate(all_issues, 1):
                category = issue.get("_category", "")
                severity = issue.get("severity", "Minor")
                issue_text = issue.get("issue", "N/A")
                example = issue.get("example", "")
                location = issue.get("location", "")
                
                # 编号
                lines.append(f"{i}. [{severity}] {category}")
                
                # 位置（如果存在）
                if location:
                    lines.append(f"   位置: {location}")
                
                # 问题（客观陈述）
                lines.append(f"   问题: {issue_text}")
                
                # 证据（如果存在）
                if example:
                    lines.append(f"   证据: {example}")
                
                lines.append("")
            
            lines.append("-" * 70)
            lines.append("请告诉我您认可纳入正式审稿的核查意见编号（如：1,2,3 或 all）")
            lines.append("-" * 70)
        
        # 第二部分：AI专业性参考观点
        ai_opinions = self.review_results.get("ai_reference_opinions", [])
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("第二部分：AI专业性参考观点")
        lines.append("(AI独立思考结论 - 仅供专家参考，不作为正式审稿依据)")
        lines.append("=" * 70)
        lines.append("")
        
        if not ai_opinions:
            lines.append("未生成专业性参考观点。")
        else:
            for i, opinion in enumerate(ai_opinions, 1):
                category = opinion.get("category", "General")
                opinion_text = opinion.get("opinion", "N/A")
                confidence = opinion.get("confidence", "Unknown")
                evidence = opinion.get("evidence", "")
                disclaimer = opinion.get("disclaimer", "")
                
                lines.append(f"{i}. [{category}]")
                lines.append(f"   观点: {opinion_text}")
                lines.append(f"   置信度: {confidence}")
                
                if evidence:
                    lines.append(f"   证据: {evidence}")
                
                lines.append(f"   {disclaimer}")
                lines.append("")
            
            lines.append("-" * 70)
            lines.append("请告诉我您认可纳入正式审稿的参考观点编号（如：1,2 或 all）")
            lines.append("-" * 70)
        
        return "\n".join(lines)


def detect_comment_duplicates(comments: List[Dict]) -> List[Dict]:
    """检测重复意见"""
    duplicates = []
    checked = set()
    
    for i, c1 in enumerate(comments):
        if c1["comment_id"] in checked:
            continue
        
        similar = []
        for j, c2 in enumerate(comments[i+1:], start=i+1):
            if c2["comment_id"] in checked:
                continue
            
            sim = calculate_similarity(c1["content"], c2["content"])
            if sim > 0.75:
                similar.append({
                    "comment_id": c2["comment_id"],
                    "similarity": round(sim, 3)
                })
                checked.add(c2["comment_id"])
        
        if similar:
            checked.add(c1["comment_id"])
            duplicates.append({
                "type": "duplicate",
                "primary_comment": c1["comment_id"],
                "duplicates": similar
            })
    
    return duplicates


def generate_conflict_report(
    db_path: str = DEFAULT_DB_FILE,
    metadata_path: str = DEFAULT_METADATA_FILE,
    pdf_path: str = None,
    output_path: str = DEFAULT_OUTPUT_FILE
) -> Dict[str, Any]:
    """生成冲突检测报告"""
    db = load_database(db_path)
    metadata = load_metadata(metadata_path)
    
    comments = db.get("comments", [])
    
    report = {
        "review_id": db.get("review_id", ""),
        "audit_time": datetime.now().isoformat(),
        "total_comments": len(comments),
        "hardcore_review_results": {},
        "ai_reference_opinions": [],
        "duplicates": [],
        "summary": {
            "total_ai_issues": 0,
            "issues_by_severity": {"Fatal": 0, "Major": 0, "Minor": 0, "Editorial": 0}
        },
        "formatted_output": ""
    }
    
    # 执行AI硬核审查
    if pdf_path and Path(pdf_path).exists():
        reviewer = HardcoreReviewer(pdf_path, metadata, comments)
        report["hardcore_review_results"] = reviewer.run_full_review()
        report["formatted_output"] = reviewer.format_review_results()
        
        # 统计
        for category, issues in report["hardcore_review_results"].items():
            if category == "ai_reference_opinions":
                report["ai_reference_opinions"] = issues
            else:
                for issue in issues:
                    severity = issue.get("severity", "Minor")
                    report["summary"]["issues_by_severity"][severity] = \
                        report["summary"]["issues_by_severity"].get(severity, 0) + 1
    
    # 检测重复意见
    report["duplicates"] = detect_comment_duplicates(comments)
    
    # 统计总数
    report["summary"]["total_ai_issues"] = sum(
        report["summary"]["issues_by_severity"].values()
    )
    
    # 保存报告
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    report["output_file"] = output_path
    return report


def main():
    parser = argparse.ArgumentParser(description="Hardcore Review for SCI Paper")
    parser.add_argument("--input", "-i", default=DEFAULT_DB_FILE, help="Input reviews database")
    parser.add_argument("--metadata", "-m", default=DEFAULT_METADATA_FILE, help="Input metadata file")
    parser.add_argument("--pdf", "-p", help="Input PDF file for hardcore review")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_FILE, help="Output conflicts report")
    
    args = parser.parse_args()
    
    try:
        result = generate_conflict_report(
            db_path=args.input,
            metadata_path=args.metadata,
            pdf_path=args.pdf,
            output_path=args.output
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
