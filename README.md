# comfyui-wordcard-maker

make word card according to html template, by using yaml defined word list and img generated.

> [!NOTE]
> This projected was created with a [cookiecutter](https://github.com/Comfy-Org/cookiecutter-comfy-extension) template. It helps you start writing custom nodes without worrying about the Python setup.

## Quickstart

1. Install [ComfyUI](https://docs.comfy.org/get_started).
1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
1. Look up this extension in ComfyUI-Manager. If you are installing manually, clone this repository under `ComfyUI/custom_nodes`.
1. Restart ComfyUI.

# Install

```
# 开发模式安装
pip install -e .
# 安装playwright浏览器
playwright install chromium
# 重启ComfyUI服务
```

## How to rewrite your word card?

`template_card.html`在与 nodes.py 同级目录下

```
src/
└── wordcard_maker/
    ├── __init__.py
    ├── nodes.py
    └── template_card.html   # ✅ 模板在这里！！其需要与generate_916_card()中的字段一一对应！！！
pyproject.toml
```

