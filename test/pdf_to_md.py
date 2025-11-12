import fitz  # PyMuPDF  
from PIL import Image  
import requests  
from tqdm import tqdm  
import os  
import io  
import datetime  

UAT = "qOwHOIifkexohLHWi7x4UNDHEtIiZjdhJUDqBWc11MvKY28XWY0Z54dB8nYvPhDA"  # 用户授权令牌  

def pillow_image_to_file_binary(image):  
    bytes_io = io.BytesIO()
    image.save(bytes_io, format='PNG')  
    return bytes_io.getvalue()  

def convert_pdf_to_images(pdf_binary, dpi=100):  
    doc = fitz.open("pdf", pdf_binary)  
    images = []  
    for i in range(doc.page_count):  
        page = doc[i]  
        pixmap = page.get_pixmap(dpi=dpi)  
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)  
        images.append(image)  
    return images  

def pdf_ocr(image):  
    api_url = "https://server.simpletex.cn/api/doc_ocr/"  
    header = {"token": UAT}  
    img_file = {"file": pillow_image_to_file_binary(image)}  
    try:
        res = requests.post(api_url, files=img_file, data={}, headers=header).json()
        if 'res' in res and 'content' in res['res']:
            return res['res']['content']
        else:
            print("OCR API 返回错误: ", res)
            return ""
    except Exception as e:
        print("请求发生错误: ", e)
        return ""

if __name__ == '__main__':  
    root_folder = r'C:\Users\anyon\Zotero\storage'  # 主文件夹路径
    today_date = datetime.date.today()

    # 遍历主文件夹下的所有子文件夹
    for subfolder in os.listdir(root_folder):
        subfolder_path = os.path.join(root_folder, subfolder)

        # 确保它是一个文件夹
        if not os.path.isdir(subfolder_path):
            continue

        # 获取子文件夹的创建时间
        folder_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(subfolder_path)).date()

        # 仅当子文件夹创建时间是今天时，才进行处理
        if folder_creation_time == today_date:
            print(f"处理今天创建的子文件夹: {subfolder_path}")

            # 遍历子文件夹中的所有 PDF 文件
            for filename in os.listdir(subfolder_path):  
                if filename.endswith('.pdf'):  
                    output_md_name = f"{os.path.splitext(filename)[0]}.md"
                    output_md_path = os.path.join(subfolder_path, output_md_name)

                    if os.path.exists(output_md_path):
                        print(f"文件 {output_md_name} 已存在，跳过转换。")
                        continue  

                    print(f"处理 {filename} ...")  
                    final_markdown_content = ""

                    with open(os.path.join(subfolder_path, filename), 'rb') as pdf_file:  
                        file_binary = pdf_file.read()  
                        images = convert_pdf_to_images(file_binary)  
                        
                        for image in tqdm(images):  
                            final_markdown_content += pdf_ocr(image) + "\n"  

                    with open(output_md_path, 'w', encoding='utf-8') as output_file:  
                        output_file.write(final_markdown_content)  
                    print(f"Markdown 已保存至 {output_md_path}")  
