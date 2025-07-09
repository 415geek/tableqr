import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# 页面设置
st.set_page_config(page_title="RestoSuite QR 桌台码生成器", layout="centered")
st.title("📦 RestoSuite QR 桌台码生成器")

# 加载字体（全部 Bold）
font_desk = ImageFont.truetype("static/NotoSansSC-Bold.ttf", 72)       # 桌号 Bold
font_shop = ImageFont.truetype("static/NotoSansSC-Bold.ttf", 48)       # 店名 Bold
font_footer = ImageFont.truetype("static/NotoSansSC-Bold.ttf", 48)     # 底部文字 Bold

# 尝试加载 logo
try:
    logo_raw = Image.open("logo.png").convert("RGBA")
    logo_img = logo_raw
except:
    logo_img = None
    st.warning("⚠️ 未找到 logo.png，标签中将省略 Logo。")

# 上传 QR 图像
qr_files = st.file_uploader("📷 上传 QR 图像（如 A1.png、B2.jpg）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# 样式定义
label_w, label_h = 720, 864  # 2.5 x 3 inch @ 288 dpi
qr_size = (400, 400)
qr_offset = (160, 130)  # 固定 QR 位置
labels_per_page = 9
cols, rows = 3, 3

# 输入店名和底部文字
shop_name = st.text_input("✏️ 输入店铺名称", "xxx火锅店")
footer_text = st.text_input("✏️ 输入底部文字（如 SCAN TO ORDER）", "SCAN TO ORDER")

# 文字位置调节（滑块，默认合理位置）
st.markdown("🎯 调整文字位置（像素单位）：")
desk_x = st.slider("桌号文字（左右调整）", 0, label_w, 290)
desk_y = st.slider("桌号文字 （上下调整）", 0, label_h, 20)
shop_x = st.slider("店铺文字 （左右调整）", 0, label_w, 200)
shop_y = st.slider("店铺文字 （上下调整）", 0, label_h, 550)
footer_x = st.slider("底部文字 （左右调整）", 0, label_w, 180)
footer_y = st.slider("底部文字 （上下调整) ", 0, label_h, 750)

# 生成单个标签
def create_label(qr_img, desk_name):
    canvas = Image.new("RGB", (label_w, label_h), "white")
    draw = ImageDraw.Draw(canvas)

    # 蓝色圆角边框 (#474FF6)
    draw.rounded_rectangle((5, 5, label_w - 5, label_h - 5), radius=40, outline="#474FF6", width=66)

    # QR（固定位置）
    qr_resized = qr_img.resize(qr_size)
    canvas.paste(qr_resized, qr_offset, qr_resized)

    # 桌号文字（Bold）
    draw.text((desk_x, desk_y), desk_name, font=font_desk, fill="black")

    # 店铺文字（Bold）
    draw.text((shop_x, shop_y), shop_name, font=font_shop, fill="black")

    # Logo（固定）
    if logo_img:
        logo_resized = logo_img.resize((160, 50))
        canvas.paste(logo_resized, ((label_w - logo_resized.width) // 2, 680), logo_resized)

    # 底部文字（Bold）
    draw.text((footer_x, footer_y), footer_text, font=font_footer, fill="black")

    return canvas

if qr_files:
    st.success(f"✅ 已上传 {len(qr_files)} 张二维码，将生成标签并分页导出")

    page_w = label_w * cols
    page_h = label_h * rows
    pages = []

    for i in range(0, len(qr_files), labels_per_page):
        canvas = Image.new("RGB", (page_w, page_h), "white")

        for idx, file in enumerate(qr_files[i:i + labels_per_page]):
            qr = Image.open(file).convert("RGBA")
            desk_name = os.path.splitext(file.name)[0]
            label = create_label(qr, desk_name)

            row, col = divmod(idx, cols)
            x = col * label_w
            y = row * label_h
            canvas.paste(label, (x, y))

        pages.append(canvas)

    # 预览
    st.subheader("🖼️ 标签预览（第1页）：")
    st.image(pages[0])

    # 导出 PDF
    pdf_bytes = BytesIO()
    pages[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pages[1:])
    st.download_button("📥 下载标签 PDF", data=pdf_bytes.getvalue(), file_name="RestoSuite_Tags.pdf", mime="application/pdf")
