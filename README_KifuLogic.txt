# KIFツリー解析プロジェクト（キフ丸）

## 処理ロジック概要

- `変化：●●手` という表記が現れたら、**それ以前に登場した最初の同一手数のノード**にぶら下げる。
- 各ノードは次の構造で保持：
  - `mainline`：本筋（最初の手）
  - `variations`：変化（分岐）

## コメント付加ルール

- 各ノードの次に複数の手がある場合（本筋＋変化）：
  - **直前のノード（分岐元）にコメントを付ける**
    - `* 本筋：▲／△ 指し手`
    - `* 変化：▲／△ 指し手`

## 実行手順（Python環境）

1. `.kif` ファイルを行単位で読み込み
2. `parse_kif_to_tree(kif_lines)` を実行してルートノードを得る
3. `root.to_string()` で整形ツリー出力

