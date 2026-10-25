import os
import base64
import yaml
from playwright.async_api import async_playwright
from inspect import cleandoc
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """清理文件名，去掉 | / \ : * ? " < > 等非法字符，zh_CN含|分割也处理"""
    bad_chars = r'|/\:*?"<> '
    for c in bad_chars:
        name = name.replace(c, "_")
    return name.strip("_")


async def generate_916_card(
    browser,
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

    page = await browser.new_page(viewport={"width": 1080, "height": 1920})
    await page.set_content(html_text)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(300)
    await page.screenshot(path=out_path, full_page=False)
    await page.close()
    print(f"✅ 竖版卡片生成成功: {out_path}")


async def generate_16_9_card(
    browser,
    img_path: str,
    en_GB: str,
    en_GB_IPA: str,
    de_DE: str,
    de_DE_IPA: str,
    fr_FR: str,
    fr_FR_IPA: str,
    it_IT: str,
    it_IT_IPA: str,
    sv_SE: str,
    sv_SE_IPA: str,
    es_ES: str,
    es_ES_IPA: str,
    ar_SA: str,
    ar_SA_IPA: str,
    ru_RU: str,
    ru_RU_IPA: str,
    out_path: str,
    html_template_text: str
):
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
    html_text = html_text.replace("{{en_GB}}", en_GB)
    html_text = html_text.replace("{{en_GB_IPA}}", en_GB_IPA)
    html_text = html_text.replace("{{de_DE}}", de_DE)
    html_text = html_text.replace("{{de_DE_IPA}}", de_DE_IPA)
    html_text = html_text.replace("{{fr_FR}}", fr_FR)
    html_text = html_text.replace("{{fr_FR_IPA}}", fr_FR_IPA)
    html_text = html_text.replace("{{it_IT}}", it_IT)
    html_text = html_text.replace("{{it_IT_IPA}}", it_IT_IPA)
    html_text = html_text.replace("{{sv_SE}}", sv_SE)
    html_text = html_text.replace("{{sv_SE_IPA}}", sv_SE_IPA)
    html_text = html_text.replace("{{es_ES}}", es_ES)
    html_text = html_text.replace("{{es_ES_IPA}}", es_ES_IPA)
    html_text = html_text.replace("{{ar_SA}}", ar_SA)
    html_text = html_text.replace("{{ar_SA_IPA}}", ar_SA_IPA)
    html_text = html_text.replace("{{ru_RU}}", ru_RU)
    html_text = html_text.replace("{{ru_RU_IPA}}", ru_RU_IPA)

    page = await browser.new_page(viewport={"width": 1920, "height": 1080})
    await page.set_content(html_text)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(300)
    await page.screenshot(path=out_path, full_page=False)
    await page.close()
    print(f"✅ 横版16:9卡片生成成功: {out_path}")


class WordCardMaker:
    """
    生词闪卡生成节点：输入yaml字符串 + 图片目录，playwright渲染；支持竖版9:16，可选横版16:9八国语言卡片
    【trigger】输入仅做时序依赖，连接SaveImage输出，保证图片全部保存磁盘后再执行本节点
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "yaml_text": ("STRING", {
                    "multiline": True,
                    "tooltip": "词条YAML对象列表文本"
                }),
                "image_output_dir": ("STRING", {
                    "default": "",
                    "tooltip": "img_00001_.png等图片存放目录，输出卡片也保存到此目录"
                }),
                "trigger": ("*", {"tooltip": "时序触发端口，连接SaveImage输出images，仅用于等待图片保存完成，不读取数据"})
            },
            "optional": {
                "generate_wide_16_9_card": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否额外生成横版16:9八国语言卡片；开启后yaml条目必须包含en_GB/de_DE等八国语言字段"
                })
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "WordCard"
    OUTPUT_NODE = True
    DESCRIPTION = cleandoc(__doc__)

    async def run(self, yaml_text: str, image_output_dir: str, trigger, generate_wide_16_9_card=False):
        this_file = Path(__file__).absolute()
        node_src_dir = this_file.parent

        # 加载竖版模板
        template_916_path = node_src_dir / "template_card.html"
        if not template_916_path.exists():
            raise FileNotFoundError(f"缺失竖版模板 template_card.html ;预期路径：{template_916_path}")
        with open(template_916_path, "r", encoding="utf-8") as f:
            html_916_template = f.read()

        # 如果开启横版，加载横版模板
        html_169_template = None
        if generate_wide_16_9_card:
            template_169_path = node_src_dir / "template_card02.html"
            if not template_169_path.exists():
                raise FileNotFoundError(f"开启横版卡片，但缺失 template_card02.html ;预期路径：{template_169_path}")
            with open(template_169_path, "r", encoding="utf-8") as f:
                html_169_template = f.read()

        # 解析yaml
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

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox"],
                env={"PWDEBUG": "0"},
            )

            for idx, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    raise ValueError(f"yaml列表第[{idx}]项不是dict词条对象")

                img_filename = f"img_{idx+1:05d}_.png"
                img_abs = target_dir / img_filename
                if not img_abs.exists():
                    raise FileNotFoundError(f"找不到对应图片：{img_abs}，yaml数组第{idx}项，期待文件名 {img_filename}")

                zhcn_raw = entry["zh_CN"]
                safe_zh = sanitize_filename(zhcn_raw)

                # -------- 生成竖版 9:16 --------
                out_916 = target_dir / f"{idx+1:02d}_{safe_zh}.png"
                await generate_916_card(
                    browser=browser,
                    img_path=str(img_abs),
                    en_US=entry["en_US"],
                    en_US_IPA=entry["en_US_IPA"],
                    zh_CN=entry["zh_CN"],
                    zh_PY=entry["zh_PY"],
                    ko_KR=entry["ko_KR"],
                    ko_RO=entry["ko_RO"],
                    jp_JP=entry["jp_JP"],
                    jp_RO=entry["jp_RO"],
                    out_path=str(out_916),
                    html_template_text=html_916_template
                )

                # -------- 如果开关打开，生成横版16:9八国语言 --------
                if generate_wide_16_9_card:
                    # 校验横版全部必填字段
                    wide_fields = [
                        "en_GB","en_GB_IPA","de_DE","de_DE_IPA",
                        "fr_FR","fr_FR_IPA","it_IT","it_IT_IPA",
                        "sv_SE","sv_SE_IPA","es_ES","es_ES_IPA",
                        "ar_SA","ar_SA_IPA","ru_RU","ru_RU_IPA"
                    ]
                    missing = [k for k in wide_fields if k not in entry]
                    if missing:
                        raise ValueError(
                            f"第[{idx}]条yaml词条缺少横版卡片字段：{','.join(missing)}\n"
                            f"如需生成横版，请补全yaml词条，或关闭generate_wide_16_9_card开关"
                        )
                    en_gb_raw = entry["en_GB"]
                    safe_en = sanitize_filename(en_gb_raw)
                    out_169 = target_dir / f"wide_{idx+1:02d}_{safe_zh}_{safe_en}.png"

                    await generate_16_9_card(
                        browser=browser,
                        img_path=str(img_abs),
                        en_GB=entry["en_GB"],
                        en_GB_IPA=entry["en_GB_IPA"],
                        de_DE=entry["de_DE"],
                        de_DE_IPA=entry["de_DE_IPA"],
                        fr_FR=entry["fr_FR"],
                        fr_FR_IPA=entry["fr_FR_IPA"],
                        it_IT=entry["it_IT"],
                        it_IT_IPA=entry["it_IT_IPA"],
                        sv_SE=entry["sv_SE"],
                        sv_SE_IPA=entry["sv_SE_IPA"],
                        es_ES=entry["es_ES"],
                        es_ES_IPA=entry["es_ES_IPA"],
                        ar_SA=entry["ar_SA"],
                        ar_SA_IPA=entry["ar_SA_IPA"],
                        ru_RU=entry["ru_RU"],
                        ru_RU_IPA=entry["ru_RU_IPA"],
                        out_path=str(out_169),
                        html_template_text=html_169_template
                    )

            await browser.close()

        print(f"===== WordCardMaker: 全部词条卡片处理完成 =====\n")
        return {}


NODE_CLASS_MAPPINGS = {
    "WordCardMaker": WordCardMaker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WordCardMaker": "生词闪卡生成器(Playwright)"
}
