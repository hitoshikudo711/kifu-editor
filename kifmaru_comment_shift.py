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

    def __repr__(self):
        return f"{self.indent * ' '}[{self.prefix}{self.move_number} {self.move_text}]"

# --- STEP 1: パース ---
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

# --- STEP 2: 平坦化 ---
def flatten_tree(node):
    flat_nodes = []
    def dfs(n):
        flat_nodes.append(n)
        for child in n.children:
            dfs(child)
    dfs(node)
    return flat_nodes

# --- STEP 3: 変化→本筋マップ作成 ---
def build_assigned_variations(flat_nodes):
    assigned = {}
    for idx, node in enumerate(flat_nodes):
        if node.prefix == "変化:":
            for j in range(idx - 1, -1, -1):
                prev = flat_nodes[j]
                if prev.prefix == "" and prev.move_number == node.move_number:
                    if prev not in assigned:
                        assigned[prev] = node
                        break
    return assigned

# --- STEP 4: コメントを前方に移動して出力 ---
def export_with_shifted_comments(root, flat_nodes, assigned_variations):
    comment_map = defaultdict(list)
    for main_node, variation_node in assigned_variations.items():
        for i in range(1, len(flat_nodes)):
            if flat_nodes[i] == main_node:
                prev_node = flat_nodes[i - 1]
                symbol = "▲" if main_node.move_number % 2 == 1 else "△"
                comment_map[prev_node].append(f"本筋：{symbol}{main_node.move_text}")
                comment_map[prev_node].append(f"変化：{symbol}{variation_node.move_text}")
                break

    def recurse_output(node, indent=0):
        lines = []
        symbol = "▲" if node.move_number % 2 == 1 else "△"
        lines.append(f"{' ' * indent}{node.move_number} {symbol}{node.move_text}")
        lines.append(f"{' ' * indent}* {symbol}{node.move_text}")
        if node in comment_map:
            for comment in comment_map[node]:
                lines.append(f"{' ' * indent}* {comment}")
        if node.children:
            lines.extend(recurse_output(node.children[0], indent + 3))
            for var in node.children[1:]:
                lines.extend(recurse_output(var, indent + 3))
        return lines

    return recurse_output(root)

# --- 実行 ---
def process_kif_tree(lines):
    root = parse_tree_from_lines(lines)
    flat_nodes = flatten_tree(root)
    assigned_variations = build_assigned_variations(flat_nodes)
    output_lines = export_with_shifted_comments(root, flat_nodes, assigned_variations)
    return output_lines
