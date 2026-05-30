#!/usr/bin/env python3
"""
State Machine Manager for SCI Paper Review System
严格控制状态转换，确保按序执行
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

STATE_FILE = "review_state.json"

STATES = {
    "PARSING": 1,
    "CONFIRMATION": 2,
    "REVIEWING": 3,
    "PARAM_COLLECTION": 4,
    "AI_AUDIT": 5,
    "REPORT_READY": 6
}

STATE_NAMES = {v: k for k, v in STATES.items()}

VALID_TRANSITIONS = {
    1: [2],      # PARSING -> CONFIRMATION
    2: [3],      # CONFIRMATION -> REVIEWING
    3: [4],      # REVIEWING -> PARAM_COLLECTION
    4: [5],      # PARAM_COLLECTION -> AI_AUDIT
    5: [6],      # AI_AUDIT -> REPORT_READY
    6: []        # REPORT_READY (terminal)
}


def load_state() -> Dict[str, Any]:
    """加载当前状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_state": 1,
        "review_id": None,
        "created_at": None,
        "updated_at": None,
        "metadata_confirmed": False,
        "params_collected": False,
        "audit_completed": False
    }


def save_state(state_data: Dict[str, Any]) -> None:
    """保存状态"""
    state_data["updated_at"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, ensure_ascii=False, indent=2)


def get_state() -> Dict[str, Any]:
    """获取当前状态"""
    state_data = load_state()
    return {
        "current_state": state_data["current_state"],
        "state_name": STATE_NAMES[state_data["current_state"]],
        "review_id": state_data["review_id"],
        "metadata_confirmed": state_data.get("metadata_confirmed", False),
        "params_collected": state_data.get("params_collected", False),
        "audit_completed": state_data.get("audit_completed", False)
    }


def validate_transition(from_state: int, to_state: int) -> tuple[bool, str]:
    """验证状态转换是否合法"""
    if from_state == to_state:
        return True, "Same state, no transition needed"
    
    if from_state not in VALID_TRANSITIONS:
        return False, f"Invalid source state: {from_state}"
    
    if to_state not in VALID_TRANSITIONS[from_state]:
        valid_next = [STATE_NAMES[s] for s in VALID_TRANSITIONS[from_state]]
        return False, f"Invalid transition from {STATE_NAMES[from_state]} to {STATE_NAMES[to_state]}. Valid next states: {valid_next}"
    
    return True, "Valid transition"


def init_session(review_id: Optional[str] = None) -> Dict[str, Any]:
    """初始化新的评审会话"""
    if review_id is None:
        review_id = f"REV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    state_data = {
        "current_state": 1,
        "review_id": review_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata_confirmed": False,
        "params_collected": False,
        "audit_completed": False
    }
    
    save_state(state_data)
    return get_state()


def set_state(new_state: int, metadata_confirmed: bool = None, 
               params_collected: bool = None, audit_completed: bool = None) -> Dict[str, Any]:
    """设置新状态（需验证合法性）"""
    state_data = load_state()
    current = state_data["current_state"]
    
    valid, msg = validate_transition(current, new_state)
    if not valid:
        return {
            "success": False,
            "error": msg,
            "current_state": current,
            "current_state_name": STATE_NAMES[current]
        }
    
    # 更新状态
    state_data["current_state"] = new_state
    
    # 更新相关标志
    if metadata_confirmed is not None:
        state_data["metadata_confirmed"] = metadata_confirmed
    if params_collected is not None:
        state_data["params_collected"] = params_collected
    if audit_completed is not None:
        state_data["audit_completed"] = audit_completed
    
    save_state(state_data)
    
    result = get_state()
    result["success"] = True
    result["message"] = f"Transitioned to {STATE_NAMES[new_state]}"
    return result


def get_allowed_actions() -> Dict[str, Any]:
    """获取当前状态下允许的操作"""
    state = load_state()["current_state"]
    
    actions = {
        1: {
            "allowed": ["init", "get_state"],
            "next_trigger": "PDF上传完成",
            "description": "等待用户上传论文PDF"
        },
        2: {
            "allowed": ["confirm", "get_state"],
            "next_trigger": "用户确认'确认/ok'",
            "description": "等待用户确认元数据"
        },
        3: {
            "allowed": ["add_comment", "finalize", "get_state"],
            "next_trigger": "用户发送'最终定稿'",
            "description": "收集审稿意见，可多轮输入"
        },
        4: {
            "allowed": ["collect_params", "get_state"],
            "next_trigger": "参数采集完成",
            "description": "收集审稿参数"
        },
        5: {
            "allowed": ["run_audit", "get_state"],
            "next_trigger": "AI审查完成",
            "description": "执行AI客观审查"
        },
        6: {
            "allowed": ["generate_report", "get_state"],
            "next_trigger": "报告生成完成",
            "description": "生成最终审稿报告"
        }
    }
    
    return actions.get(state, {"allowed": [], "error": "Unknown state"})


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(json.dumps(get_state(), ensure_ascii=False, indent=2))
        sys.exit(0)
    
    action = sys.argv[1]
    
    if action == "--action":
        if len(sys.argv) < 3:
            print("Error: --action requires a subcommand")
            sys.exit(1)
        action = sys.argv[2]
    
    if action == "get_state":
        result = get_state()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif action == "init":
        review_id = None
        if len(sys.argv) > 2 and sys.argv[2] == "--review_id":
            review_id = sys.argv[3] if len(sys.argv) > 3 else None
        result = init_session(review_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif action == "validate":
        if len(sys.argv) < 4:
            print("Error: validate requires from_state and to_state")
            sys.exit(1)
        from_s = int(sys.argv[2])
        to_s = int(sys.argv[3])
        valid, msg = validate_transition(from_s, to_s)
        print(json.dumps({"valid": valid, "message": msg}, ensure_ascii=False, indent=2))
        
    elif action == "set_state":
        if len(sys.argv) < 3:
            print("Error: set_state requires new_state number")
            sys.exit(1)
        new_state = int(sys.argv[2])
        result = set_state(new_state)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif action == "allowed_actions":
        result = get_allowed_actions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
