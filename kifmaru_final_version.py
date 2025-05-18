import re
from collections import defaultdict

class TreeNode:
    def __init__(self, move_number, move_text, indent=0, prefix=""):
        self.move_number = move_number
        self.move_text = move_text
        self.indent = indent
        self.children = []
        self.prefix = prefix
        self.comment = None

# --- ツリー構造解析 ---
def parse_tree_from_lines(lines):
    move_line_pattern = re.compile(r'^( *)(変化: )?(\d+)\s+(.+)$')
    stack = []
    root = None
    for line in lines:
        match = move_line_pattern.match(line)
        if not match:
            continue
        indent = len(match.group(1))
        prefix = match.group(2) or ""
        move_number = int(match.group(3))
        move_text = match.group(4)
        node = TreeNode(move_number, move_text, indent, prefix.strip())
        while stack and stack[-1].indent >= indent:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            root = node
        stack.append(node)
    return root

# --- DFS 展開 ---
def flatten_tree(root):
    result = []
    def dfs(node):
        result.append(node)
        for child in node.children:
            dfs(child)
    dfs(root)
    return result

# --- 変化と本筋を1対1でマッピング ---
def assign_variations(flat_nodes):
    assigned = {}
    for i, node in enumerate(flat_nodes):
        if node.prefix == "変化":
            for j in range(i - 1, -1, -1):
                candidate = flat_nodes[j]
                if candidate.prefix == "" and candidate.move_number == node.move_number:
                    if candidate not in assigned:
                        assigned[candidate] = node
                        break
    return assigned

# --- ノード単位の注釈を構築 ---
def build_comment_map(flat_nodes, assigned_variations):
    comment_map = defaultdict(list)
    for node in flat_nodes:
        symbol = "▲" if node.move_number % 2 == 1 else "△"
        comment_map[node].append(f"* {symbol}{node.move_text}")  # 指し手
    for i, node in enumerate(flat_nodes):
        if node in assigned_variations:
            variation = assigned_variations[node]
            if i > 0:
                prev_node = flat_nodes[i - 1]
                symbol = "▲" if node.move_number % 2 == 1 else "△"
                comment_map[prev_node].append(f"* 本筋：{symbol}{node.move_text}")
                comment_map[prev_node].append(f"* 変化：{symbol}{variation.move_text}")
    return comment_map

# --- 元KIFに対応づけて注釈を挿入 ---
def merge_comments_into_kif(original_lines, flat_nodes, comment_map):
    move_line_pattern = re.compile(r'^(\d+)\s+(.+)$')
    output = []
    kif_index = 0
    flat_index = 0
    while kif_index < len(original_lines) and flat_index < len(flat_nodes):
        line = original_lines[kif_index]
        move_match = move_line_pattern.match(line.strip())
        if move_match:
            move_number = int(move_match.group(1))
            node = flat_nodes[flat_index]
            if node.move_number == move_number:
                output.append(line)
                if node in comment_map:
                    output.extend(comment_map[node])
                flat_index += 1
            else:
                output.append(line)
            kif_index += 1
        else:
            output.append(line)
            kif_index += 1
    output.extend(original_lines[kif_index:])
    return output
