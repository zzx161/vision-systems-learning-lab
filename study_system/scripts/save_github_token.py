#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
from pathlib import Path


TOKEN_DIR = Path.home() / ".config" / "vision-systems-learning-lab"
TOKEN_FILE = TOKEN_DIR / "github_token"


def main() -> None:
    print("请输入新的 GitHub Personal Access Token。")
    print("注意：不要使用已经在聊天里暴露过的旧 token。")
    token = input("PAT: ").strip()
    if not token:
        raise SystemExit("未输入 token，已取消。")

    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    print(f"已保存到: {TOKEN_FILE}")
    print("权限已设置为仅当前用户可读写。")


if __name__ == "__main__":
    main()
