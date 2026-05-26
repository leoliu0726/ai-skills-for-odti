#!/usr/bin/env python3
"""
Review Storage Manager for SCI Paper Review System
结构化存储审稿意见，支持多轮添加、更新、导出
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

DEFAULT_DB_FILE = "reviews.json"
COMMENT_COUNTER_FILE = "comment_counter.json"


def load_database(db_path: str = DEFAULT_DB_FILE) -> Dict[str, Any]:
    """加载审稿数据库"""
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 返回默认空结构
    return {
        "review_id": "",
        "paper_metadata": {},
        "comments": [],
        "ai_comments": [],
        "params": {},
        "current_state": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def save_database(db: Dict[str, Any], db_path: str = DEFAULT_DB_FILE) -> None:
    """保存审稿数据库"""
    db["updated_at"] = datetime.now().isoformat()
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, ensure_ascii=False, indent=2)


def load_metadata(metadata_path: str = "metadata.json") -> Dict[str, Any]:
    """加载论文元数据"""
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_params(params_path: str = "params.json") -> Dict[str, Any]:
    """加载审稿参数"""
    if os.path.exists(params_path):
        with open(params_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_next_comment_id(comments: List[Dict], prefix: str = "C") -> str:
    """生成下一个评论ID"""
    max_num = 0
    for c in comments:
        cid = c.get("comment_id", "")
        if cid.startswith(prefix):
            try:
                num = int(cid[len(prefix):])
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"{prefix}{max_num + 1:03d}"


def get_next_ai_comment_id(ai_comments: List[Dict]) -> str:
    """生成下一个AI评论ID"""
    return get_next_comment_id(ai_comments, "AI_C")


def add_comment(
    content: str,
    severity: str = "Minor",
    category: str = "General",
    location: str = "",
    evidence: str = "",
    source: str = "Manual",
    comment_type: str = "formal",
    db_path: str = DEFAULT_DB_FILE,
    metadata_path: str = "metadata.json",
    params_path: str = "params.json"
) -> Dict[str, Any]:
    """添加审稿意见"""
    db = load_database(db_path)
    
    # 初始化
    if not db["review_id"]:
        db["review_id"] = f"REV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 加载关联数据
    db["paper_metadata"] = load_metadata(metadata_path)
    db["params"] = load_params(params_path)
    
    # 创建评论
    comment = {
        "comment_id": get_next_comment_id(db["comments"]),
        "severity": severity,
        "category": category,
        "location": location,
        "source": source,
        "type": comment_type,
        "content": content,
        "evidence": evidence,
        "ai_reference": False,
        "timestamp": datetime.now().isoformat()
    }
    
    db["comments"].append(comment)
    save_database(db, db_path)
    
    return {
        "success": True,
        "saved_comment": comment,
        "total_comments": len(db["comments"]),
        "message": f"Comment [{comment['comment_id']}] saved successfully"
    }


def add_ai_reference(
    content: str,
    uncertain: bool = False,
    db_path: str = DEFAULT_DB_FILE
) -> Dict[str, Any]:
    """添加AI参考意见"""
    db = load_database(db_path)
    
    ai_comment = {
        "comment_id": get_next_ai_comment_id(db["ai_comments"]),
        "content": content,
        "ai_reference": True,
        "uncertain": uncertain,
        "timestamp": datetime.now().isoformat()
    }
    
    db["ai_comments"].append(ai_comment)
    save_database(db, db_path)
    
    return {
        "success": True,
        "saved_ai_comment": ai_comment,
        "total_ai_comments": len(db["ai_comments"]),
        "message": f"AI reference [{ai_comment['comment_id']}] saved successfully"
    }


def list_comments(
    db_path: str = DEFAULT_DB_FILE,
    severity_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    source_filter: Optional[str] = None
) -> Dict[str, Any]:
    """列出审稿意见"""
    db = load_database(db_path)
    
    comments = db["comments"]
    
    # 应用过滤
    if severity_filter:
        comments = [c for c in comments if c.get("severity") == severity_filter]
    if category_filter:
        comments = [c for c in comments if c.get("category") == category_filter]
    if source_filter:
        comments = [c for c in comments if c.get("source") == source_filter]
    
    return {
        "success": True,
        "review_id": db["review_id"],
        "comments": comments,
        "ai_comments": db["ai_comments"],
        "total_formal_comments": len([c for c in db["comments"] if c.get("type") == "formal"]),
        "total_ai_comments": len(db["ai_comments"]),
        "by_severity": {
            "Fatal": len([c for c in db["comments"] if c.get("severity") == "Fatal"]),
            "Major": len([c for c in db["comments"] if c.get("severity") == "Major"]),
            "Minor": len([c for c in db["comments"] if c.get("severity") == "Minor"]),
            "Editorial": len([c for c in db["comments"] if c.get("severity") == "Editorial"])
        },
        "by_category": list(set(c.get("category") for c in db["comments"]))
    }


def update_comment(
    comment_id: str,
    updates: Dict[str, Any],
    db_path: str = DEFAULT_DB_FILE
) -> Dict[str, Any]:
    """更新审稿意见"""
    db = load_database(db_path)
    
    found = False
    for i, c in enumerate(db["comments"]):
        if c["comment_id"] == comment_id:
            db["comments"][i].update(updates)
            db["comments"][i]["timestamp"] = datetime.now().isoformat()
            found = True
            break
    
    if not found:
        return {
            "success": False,
            "error": f"Comment {comment_id} not found"
        }
    
    save_database(db, db_path)
    return {
        "success": True,
        "updated_comment": db["comments"][i],
        "message": f"Comment [{comment_id}] updated successfully"
    }


def delete_comment(
    comment_id: str,
    db_path: str = DEFAULT_DB_FILE
) -> Dict[str, Any]:
    """删除审稿意见"""
    db = load_database(db_path)
    
    original_count = len(db["comments"])
    db["comments"] = [c for c in db["comments"] if c["comment_id"] != comment_id]
    
    if len(db["comments"]) == original_count:
        return {
            "success": False,
            "error": f"Comment {comment_id} not found"
        }
    
    save_database(db, db_path)
    return {
        "success": True,
        "message": f"Comment [{comment_id}] deleted successfully",
        "remaining_comments": len(db["comments"])
    }


def export_comments(
    output_format: str = "json",
    db_path: str = DEFAULT_DB_FILE,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """导出审稿意见"""
    db = load_database(db_path)
    
    if output_format == "json":
        export_data = {
            "review_id": db["review_id"],
            "paper_metadata": db["paper_metadata"],
            "comments": db["comments"],
            "ai_comments": db["ai_comments"],
            "params": db["params"],
            "exported_at": datetime.now().isoformat()
        }
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
        
    elif output_format == "text":
        lines = [
            f"SCI Paper Review Report",
            f"Review ID: {db['review_id']}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 60,
            ""
        ]
        
        # 按严重性分组
        for severity in ["Fatal", "Major", "Minor", "Editorial"]:
            severity_comments = [c for c in db["comments"] if c.get("severity") == severity]
            if severity_comments:
                lines.append(f"\n## {severity} Issues ({len(severity_comments)})")
                lines.append("-" * 40)
                for c in severity_comments:
                    lines.append(f"\n[{c['comment_id']}] {c['category']}")
                    lines.append(f"Location: {c.get('location', 'N/A')}")
                    lines.append(f"Comment: {c['content']}")
                    if c.get('evidence'):
                        lines.append(f"Evidence: {c['evidence']}")
        
        content = "\n".join(lines)
    
    else:
        return {
            "success": False,
            "error": f"Unsupported format: {output_format}"
        }
    
    # 保存或输出
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            "success": True,
            "output_path": output_path,
            "format": output_format
        }
    else:
        return {
            "success": True,
            "content": content,
            "format": output_format
        }


def main():
    parser = argparse.ArgumentParser(description="Review Storage Manager")
    parser.add_argument("--action", "-a", required=True, 
                        choices=["add", "add_ai", "list", "update", "delete", "export"],
                        help="Action to perform")
    parser.add_argument("--db", default=DEFAULT_DB_FILE, help="Database file path")
    parser.add_argument("--metadata", default="metadata.json", help="Metadata file path")
    parser.add_argument("--params", default="params.json", help="Params file path")
    
    # add参数
    parser.add_argument("--content", help="Comment content")
    parser.add_argument("--severity", default="Minor", 
                        choices=["Fatal", "Major", "Minor", "Editorial"],
                        help="Severity level")
    parser.add_argument("--category", default="General", help="Category")
    parser.add_argument("--location", default="", help="Location in paper")
    parser.add_argument("--evidence", default="", help="Evidence")
    parser.add_argument("--source", default="Manual", help="Source: Manual/AI")
    
    # add_ai参数
    parser.add_argument("--uncertain", action="store_true", help="Mark as uncertain")
    
    # list参数
    parser.add_argument("--filter-severity", help="Filter by severity")
    parser.add_argument("--filter-category", help="Filter by category")
    parser.add_argument("--filter-source", help="Filter by source")
    
    # update参数
    parser.add_argument("--comment-id", help="Comment ID to update")
    parser.add_argument("--updates", help="JSON string of updates")
    
    # delete参数
    parser.add_argument("--delete-id", help="Comment ID to delete")
    
    # export参数
    parser.add_argument("--format", default="json", choices=["json", "text"],
                        help="Export format")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        if args.action == "add":
            if not args.content:
                print("Error: --content required for add action")
                sys.exit(1)
            result = add_comment(
                content=args.content,
                severity=args.severity,
                category=args.category,
                location=args.location,
                evidence=args.evidence,
                source=args.source,
                db_path=args.db,
                metadata_path=args.metadata,
                params_path=args.params
            )
            
        elif args.action == "add_ai":
            if not args.content:
                print("Error: --content required for add_ai action")
                sys.exit(1)
            result = add_ai_reference(
                content=args.content,
                uncertain=args.uncertain,
                db_path=args.db
            )
            
        elif args.action == "list":
            result = list_comments(
                db_path=args.db,
                severity_filter=args.filter_severity,
                category_filter=args.filter_category,
                source_filter=args.filter_source
            )
            
        elif args.action == "update":
            if not args.comment_id:
                print("Error: --comment-id required for update action")
                sys.exit(1)
            updates = json.loads(args.updates) if args.updates else {}
            result = update_comment(
                comment_id=args.comment_id,
                updates=updates,
                db_path=args.db
            )
            
        elif args.action == "delete":
            if not args.delete_id:
                print("Error: --delete-id required for delete action")
                sys.exit(1)
            result = delete_comment(
                comment_id=args.delete_id,
                db_path=args.db
            )
            
        elif args.action == "export":
            result = export_comments(
                output_format=args.format,
                db_path=args.db,
                output_path=args.output
            )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
