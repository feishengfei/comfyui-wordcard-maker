import os
import base64
import yaml
from playwright.sync_api import sync_playwright
from inspect import cleandoc
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """清理文件名，去掉 | / \ : * ? " < > 等非法字符，zh_CN含|分割也处理"""
    bad_chars = r'|/\:*?"<> '
    for c in bad_chars:
        name = name.replace(c, "_")
    return name.strip("_")


def generate_916_card(
    img_path: str,
    en_US: str,
    en_US_IPA: str,
    zh_CN: str,
    zh_PY: str,
    ko_KR: str,
    ko_RO: str,
    jp_JP: str,
    jp_RO: str,
    out_path: str,
    html_template_text: str
):
    # 读取图片，转为base64 data‑url
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    ext = os.path.splitext(img_path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }
    mime = mime_map.get(ext, "image/png")
    b64_data = base64.b64encode(img_bytes).decode("utf‑8")
    img_data_url = f"data:{mime};base64,{b64_data}"

    html_text = html_template_text
    html_text = html_text.replace("{{IMG_BASE64}}", img_data_url)
    html_text = html_text.replace("{{en_US}}", en_US)
    html_text = html_text.replace("{{en_US_IPA}}", en_US_IPA)
    html_text = html_text.replace("{{zh_CN}}", zh_CN)
    html_text = html_text.replace("{{zh_PY}}", zh_PY)
    html_text = html_text.replace("{{ko_KR}}", ko_KR)
    html_text = html_text.replace("{{ko_RO}}", ko_RO)
    html_text = html_text.replace("{{jp_JP}}", jp_JP)
    html_text = html_text.replace("{{jp_RO}}", jp_RO)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(html_text)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        page.screenshot(path=out_path, full_page=False)
        browser.close()
    print(f"✅ 卡片生成成功: {out_path}")


class WordCardMaker:
    """
    生词闪卡生成节点：输入yaml字符串 + 图片目录，调用playwright渲染template_card.html生成词汇卡片PNG
    【trigger】输入仅做时序依赖，连接SaveImage输出，保证图片全部保存磁盘后再执行本节点
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "yaml_text": ("STRING", {
                    "multiline": True,
                    "tooltip": "词条YAML对象列表文本，和card_00001_.yaml内容一致"
                }),
                "image_output_dir": ("STRING", {
                    "default": "",
                    "tooltip": "img_00001_.png等图片存放目录，输出卡片也保存到此目录"
                }),
                "trigger": ("*", {"tooltip": "时序触发端口，连接SaveImage输出images，仅用于等待图片保存完成，不读取数据"})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "WordCard"
    OUTPUT_NODE = True  # 标记输出节点，即使无返回tuple，comfyui也会执行
    DESCRIPTION = cleandoc(__doc__)

    def run(self, yaml_text: str, image_output_dir: str, trigger):
        # -------- 1.加载html模板文件，模板放在本节点源码目录 --------
        # 当前nodes.py文件所在目录
        this_file = Path(__file__).absolute()
        node_src_dir = this_file.parent
        template_path = node_src_dir / "template_card.html"
        if not template_path.exists():
            raise FileNotFoundError(f"节点源码目录缺失 template_card.html ;预期路径：{template_path}")
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()

        # -------- 2.解析yaml字符串 --------
        try:
            entries = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML文本解析失败：{str(e)}") from e

        if not isinstance(entries, list):
            raise ValueError("yaml_text必须是对象列表，以 `-` 开头数组")

        target_dir = Path(image_output_dir).absolute()
        if not target_dir.exists():
            raise NotADirectoryError(f"图片输出目录不存在：{target_dir}")

        print(f"\n===== WordCardMaker: 开始处理，目标目录 {target_dir} =====")

        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"yaml列表第[{idx}]项不是dict词条对象")

            # 原图文件名：img_00001_.png，索引从1开始
            img_filename = f"img_{idx+1:05d}_.png"
            img_abs = target_dir / img_filename
            if not img_abs.exists():
                raise FileNotFoundError(f"找不到对应图片：{img_abs}，yaml数组第{idx}项，期待文件名 {img_filename}")

            zhcn_raw = entry["zh_CN"]
            safe_name = sanitize_filename(zhcn_raw)
            out_filename = f"{safe_name}.png"
            out_abs = target_dir / out_filename

            generate_916_card(
                img_path=str(img_abs),
                en_US=entry["en_US"],
                en_US_IPA=entry["en_US_IPA"],
                zh_CN=entry["zh_CN"],
                zh_PY=entry["zh_PY"],
                ko_KR=entry["ko_KR"],
                ko_RO=entry["ko_RO"],
                jp_JP=entry["jp_JP"],
                jp_RO=entry["jp_RO"],
                out_path=str(out_abs),
                html_template_text=html_template
            )
        print(f"===== WordCardMaker: 全部词条卡片处理完成 =====\n")
        return {}


NODE_CLASS_MAPPINGS = {
    "WordCardMaker": WordCardMaker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WordCardMaker": "生词闪卡生成器(Playwright)"
}
