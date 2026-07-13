#!/usr/bin/env python3
"""Use DeepSeek API to batch optimize MD files for readability."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是一个对客操作手册的优化专家。读者是一线网点、中心、云仓或网络货运人员，他们需要按文档完成系统操作。你的任务是把从钉钉导出的 Markdown 优化成稳定、清晰、可重复生成的操作手册。

直接输出优化后的 Markdown，不要加任何解释说明。不要编造业务规则；不确定的信息用谨慎、通用的表述。

## 必须保留
1. 保留原文业务含义、菜单名称、按钮名称、金额、时间、频率、状态、编码、截图和链接。
2. 保持图片引用 `![xxx](path)` 的路径不变，不要删除、改名或移动图片。
3. 保持代码块、表格和原有关键字段不变。
4. 保留唯一 H1 和已有 frontmatter；不要输出 ``` 包裹。

## 操作手册结构
尽量整理为以下结构；原文已有对应内容时合并进去，缺失且无法判断时可给简短通用说明，不要硬编具体规则：

# 标题

## 适用场景
说明什么情况下看本文。

## 前置条件
说明账号、权限、数据、设备等准备项。

## 操作入口
写清系统路径或入口；如果原文没有明确入口，写“请以系统实际菜单路径为准”。

## 操作步骤
用 1. 2. 3. 有序步骤组织，步骤中保留截图位置。

## 操作结果
说明完成后应看到什么状态、单据或结果。

## 注意事项
整理限制、权限、时间、金额、异常等提醒。

## 常见问题
只根据原文能推断的问题整理；没有就不要强行编造。

## 内容优化规则
1. 用更清晰、更口语化的方式表述操作步骤，降低理解门槛。
2. 保留原意，但可以把冗长啰嗦的句子改短。
3. 关键信息（按钮名称、菜单路径、数值、时间、频率）用 **加粗** 标注。
4. 删除无意义的串场废话，例如“接下来我们一起来看看”。
5. 对含糊描述可用括号补充解释，但必须基于原文上下文。
6. 如果是“先 A 再 B”的流程，改成步骤化的有序列表。

## 格式规则
1. 保留唯一一级标题（H1），其余重复 H1 下沉为 H2，H2 下沉为 H3。
2. 剥离标题中的旧编号前缀，如“第一步：”“①”“1.”。
3. [灯泡] → 💡、[警告] → ⚠️、[必知必读] → 📌、[星星转动] → ✨、[魔法棒挥动] → 🪄、[握手] → 🤝、[流泪] → 😢、[跳舞] → 💃、[加油] → 💪、[你强] → 👍。
4. 强调样式使用 VitePress 容器语法：
   - 提示、说明、步骤、补充说明 → ::: tip 标题\\n内容\\n:::
   - 注意、ps、注、注释、备注 → ::: warning 注意事项\\n内容\\n:::
   - 仅、必须、不可、禁止、不允许、限制、校验等关键规则 → ::: danger 重点提醒\\n内容\\n:::
5. 相邻同类型容器要合并。
6. H4 及更深层级标题压成列表项或正文小标题。"""


def optimize(md_text: str, model: str = DEFAULT_MODEL) -> str:
    if not API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is required when --use-ai is enabled")

    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": md_text},
            ],
            "temperature": 0.1,
            "max_tokens": 8192,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```markdown"):
        content = content[len("```markdown"):]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def discover_md_files(root: Path) -> list[Path]:
    exclude = {".git", "__pycache__", ".pytest_cache", ".ruff_cache",
               "site", ".venv", "venv", "node_modules", "skills", "docs"}
    found: list[Path] = []
    def walk(d: Path) -> None:
        for child in sorted(d.iterdir()):
            if child.name in exclude:
                continue
            if child.is_dir():
                walk(child)
            elif child.suffix.lower() == ".md":
                found.append(child)
    walk(root)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", default="output")
    parser.add_argument("-o", "--output", default="output_optimized")
    parser.add_argument("-n", "--limit", type=int, default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"DeepSeek model (default: {DEFAULT_MODEL})")
    parser.add_argument("--retry", type=int, default=3)
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip files that already exist in output dir")
    parser.add_argument("--no-skip", action="store_true", default=False,
                        help="Do not skip existing files")
    args = parser.parse_args()

    src_dir = Path(args.source).resolve()
    dst_dir = Path(args.output).resolve()
    skip_existing = args.skip_existing and not args.no_skip

    md_files = discover_md_files(src_dir)
    if not md_files:
        print("No MD files found.")
        sys.exit(1)

    if skip_existing:
        before = len(md_files)
        md_files = [f for f in md_files if not (dst_dir / f.relative_to(src_dir)).exists()]
        skipped = before - len(md_files)
        if skipped:
            print(f"Skipped {skipped} existing files.")

    if args.limit:
        md_files = md_files[:args.limit]

    if not md_files:
        print("All files already processed.")
        sys.exit(0)

    print(f"Optimizing {len(md_files)} files -> {dst_dir}")

    failed: list[str] = []
    for idx, src in enumerate(md_files, 1):
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        md_text = src.read_text(encoding="utf-8", errors="ignore")
        if len(md_text.strip()) < 10:
            dst.write_text(md_text, encoding="utf-8")
            continue

        for attempt in range(1, args.retry + 1):
            try:
                result = optimize(md_text, model=args.model)
                dst.write_text(result, encoding="utf-8")
                break
            except Exception as e:
                print(f"  [{idx}/{len(md_files)}] FAILED {rel} (attempt {attempt}): {e}")
                if attempt == args.retry:
                    failed.append(str(rel))
                    dst.write_text(md_text, encoding="utf-8")
                else:
                    time.sleep(2)

        if idx % 10 == 0 or idx == len(md_files):
            print(f"  [{idx}/{len(md_files)}] done")

    import shutil
    for img_dir in src_dir.rglob("images"):
        if img_dir.is_dir():
            rel_img = img_dir.relative_to(src_dir)
            dst_img = dst_dir / rel_img
            if not dst_img.exists():
                shutil.copytree(img_dir, dst_img)

    print(f"Done! {len(md_files) - len(failed)}/{len(md_files)} optimized.")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
