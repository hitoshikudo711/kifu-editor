import re

class Node:
    def __init__(self, move_number, move_text, comment=None):
        self.move_number = move_number
        self.move_text = move_text
        self.comment = comment
        self.mainline = None
        self.variations = []

    def add_variation(self, variation_node):
        self.variations.append(variation_node)

    def to_string(self, indent=0, prefix=""):
        pad = " " * indent
        result = f"{pad}{prefix}{self.move_number} {self.move_text}"
        if self.comment:
            result += f"  *{self.comment}"
        result += "\n"
        if self.mainline:
            result += self.mainline.to_string(indent + 3)
        for var in self.variations:
            result += var.to_string(indent + 3, "変化: ")
        return result

def parse_kif_to_tree(kif_lines):
    move_pattern = re.compile(r'^\s*(\d+)\s+(.+)$')
    variation_pattern = re.compile(r'^変化[:：]\s*(\d+)手')

    all_nodes = []
    node_history = []
    variation_moves = []
    variation_target = None
    pending_comments = []
    in_variation = False

    def attach_variation(variation_moves, target_number):
        for base_node in reversed(node_history):
            if base_node.move_number == target_number:
                base_node.add_variation(variation_moves[0])
                for i in range(len(variation_moves) - 1):
                    variation_moves[i].mainline = variation_moves[i + 1]
                node_history.extend(variation_moves)
                break

    for line in kif_lines:
        line = line.strip()
        if line.startswith("*"):
            pending_comments.append(line.lstrip("*").strip())
            continue
        if match := variation_pattern.match(line):
            if variation_moves and variation_target is not None:
                attach_variation(variation_moves, variation_target)
            in_variation = True
            variation_target = int(match.group(1))
            variation_moves = []
            pending_comments = []
            continue
        if match := move_pattern.match(line):
            move_number = int(match.group(1))
            move_text = match.group(2)
            comment = "\n".join(pending_comments) if pending_comments else None
            pending_comments = []
            node = Node(move_number, move_text, comment)
            if in_variation:
                variation_moves.append(node)
            else:
                if all_nodes:
                    all_nodes[-1].mainline = node
                all_nodes.append(node)
                node_history.append(node)

    if variation_moves and variation_target is not None:
        attach_variation(variation_moves, variation_target)

    return all_nodes[0]
