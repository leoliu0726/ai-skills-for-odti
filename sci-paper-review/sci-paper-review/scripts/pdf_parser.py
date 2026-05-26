#!/usr/bin/env python3
"""
PDF Parser for SCI Paper Review System - 延迟加载版本
仅解析封面+摘要，极速启动，按需加载方法/结论
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Run: pip install PyMuPDF==1.23.8")
    sys.exit(1)


# 预编译正则表达式
RE_ABSTRACT = re.compile(
    r'Abstract[:\s]*(.*?)(?=\n\s*(?:Keywords|Introduction|1\.|I\.)|$)',
    re.DOTALL | re.IGNORECASE
)
RE_KEYWORDS = re.compile(
    r'Keywords[:\s]*(.*?)(?=\n\s*(?:Abstract|Introduction|1\.|I\.)|$)',
    re.DOTALL | re.IGNORECASE
)
RE_METHODS = re.compile(
    r'(?:Methods?|Methodology|Experimental|Experimental Section|Materials and Methods)(.*?)(?=\n\s*(?:Results|Discussion|Conclusion|$))',
    re.DOTALL | re.IGNORECASE
)
RE_CONCLUSION = re.compile(
    r'(?:Conclusion|Conclusions|Summary)(.*?)(?=\n\s*(?:Acknowledgments|References|$))',
    re.DOTALL | re.IGNORECASE
)
RE_JOURNAL = re.compile(
    r'(Nature|Science|Cell|PNAS|PRL|Nano Letters|ACS|Advanced Materials|IEEE|Elsevier|Springer|Nat\.|Sci\.)',
    re.IGNORECASE
)


def fast_extract_cover(pdf_path: str) -> dict:
    """
    快速提取：仅封面信息（前3页）
    用于State 1初始化
    """
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    
    # 封面文本（只取前3页）
    cover_text = ""
    for page in doc[:min(3, page_count)]:
        cover_text += page.get_text() + "\n"
    
    doc_metadata = doc.metadata
    doc.close()
    
    metadata = {
        "file_name": Path(pdf_path).name,
        "file_size": Path(pdf_path).stat().st_size,
        "page_count": page_count,
        "title": "",
        "authors": [],
        "journal": "",
        "doi": "",
        "abstract": "",
        "keywords": [],
        "research_area": "",
        "extraction_mode": "fast",
        "extracted_at": datetime.now().isoformat()
    }
    
    # 标题：从元数据
    if doc_metadata.get("title"):
        metadata["title"] = doc_metadata["title"].strip()
    
    # 作者：从元数据
    if doc_metadata.get("author"):
        authors_str = doc_metadata["author"]
        metadata["authors"] = [a.strip() for a in re.split(r'[,;]|\band\b', authors_str) if a.strip()]
    
    # DOI：从元数据
    if doc_metadata.get("doi"):
        metadata["doi"] = doc_metadata["doi"].strip()
    
    # 标题备用：从封面首行
    if not metadata["title"] and cover_text:
        first_line = cover_text.strip().split('\n')[0].strip()
        if 10 < len(first_line) < 300:
            metadata["title"] = first_line
    
    # 摘要
    abstract_match = RE_ABSTRACT.search(cover_text)
    if abstract_match:
        metadata["abstract"] = abstract_match.group(1).strip()[:2000]
    
    # 关键词
    keywords_match = RE_KEYWORDS.search(cover_text)
    if keywords_match:
        kw_text = keywords_match.group(1)
        metadata["keywords"] = [k.strip() for k in re.split(r'[,;]', kw_text) if k.strip()]
    
    # 研究领域
    if metadata["keywords"]:
        metadata["research_area"] = "; ".join(metadata["keywords"][:5])
    
    # 期刊识别
    journal_match = RE_JOURNAL.search(cover_text[:1000])
    if journal_match:
        metadata["journal"] = journal_match.group(1)
    
    return metadata


def extract_methods(pdf_path: str) -> str:
    """
    按需提取方法章节
    用于State 5 AI审查
    """
    doc = fitz.open(pdf_path)
    
    # 扫描前80%页面查找方法章节
    scan_limit = int(len(doc) * 0.8)
    full_text = ""
    for page in doc[:scan_limit]:
        full_text += page.get_text() + "\n"
    
    doc.close()
    
    match = RE_METHODS.search(full_text)
    if match:
        return match.group(0)[:3000]
    return ""


def extract_conclusion(pdf_path: str) -> str:
    """
    按需提取结论章节
    用于State 5 AI审查
    """
    doc = fitz.open(pdf_path)
    
    # 扫描后50%页面查找结论
    start_page = int(len(doc) * 0.5)
    full_text = ""
    for page in doc[start_page:]:
        full_text += page.get_text() + "\n"
    
    doc.close()
    
    match = RE_CONCLUSION.search(full_text)
    if match:
        return match.group(0)[:3000]
    return ""


def extract_full_text(pdf_path: str, max_pages: int = None) -> str:
    """
    提取全文（用于AI审查）
    限制页数以控制token消耗
    """
    doc = fitz.open(pdf_path)
    
    if max_pages is None:
        max_pages = len(doc)
    
    # 智能采样：封面+均匀分布采样
    if max_pages <= 10:
        page_indices = list(range(min(max_pages, len(doc))))
    else:
        # 每隔N页取样，保持覆盖
        step = max(1, len(doc) // max_pages)
        page_indices = list(range(0, len(doc), step))[:max_pages]
    
    full_text = ""
    for idx in page_indices:
        full_text += doc[idx].get_text() + "\n"
        full_text += f"[Page {idx + 1}]\n"
    
    doc.close()
    return full_text


def validate_metadata(metadata: dict) -> list:
    """验证元数据完整性"""
    issues = []
    
    if not metadata.get("title"):
        issues.append("Title not extracted - please verify manually")
    
    if not metadata.get("authors"):
        issues.append("Authors not extracted - please verify manually")
    
    if not metadata.get("abstract"):
        issues.append("[Uncertain] Abstract not detected - please verify")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="Extract metadata from SCI paper PDF")
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", default="metadata.json", help="Output JSON file path")
    parser.add_argument("--mode", "-m", default="fast", choices=["fast", "full"],
                       help="Extraction mode: fast (cover only) or full (all sections)")
    parser.add_argument("--validate", action="store_true", help="Validate extracted metadata")
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)
    
    try:
        if args.mode == "fast":
            metadata = fast_extract_cover(args.input)
        else:
            # 完整解析模式
            metadata = fast_extract_cover(args.input)
            metadata["methodology"] = extract_methods(args.input)
            metadata["conclusion"] = extract_conclusion(args.input)
            metadata["extraction_mode"] = "full"
        
        # 验证
        validation_issues = []
        if args.validate:
            validation_issues = validate_metadata(metadata)
        
        # 保存
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        result = {
            "success": True,
            "metadata": metadata,
            "validation_issues": validation_issues
        }
        
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
