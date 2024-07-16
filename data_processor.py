
import os
from magic_pdf.cli import magicpdf
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter
from pathlib import Path
import html2text
import os
import cv2
from paddleocr import PPStructure, save_structure_res
from paddleocr import PaddleOCR
import json


def read_fn(path):
    disk_rw = DiskReaderWriter(os.path.dirname(path))
    return disk_rw.read(os.path.basename(path), AbsReaderWriter.MODE_BIN)


def html_to_markdown(html_content):
    """
    将 HTML 内容转换为 Markdown 格式
    参数:
    html_content (str): HTML 内容字符串
    返回:
    str: 转换后的 Markdown 字符串
    """
    # 创建一个 html2text 的 HTML2Text 对象
    h = html2text.HTML2Text()
    # 设置一些选项（如是否保留链接）
    h.ignore_links = False
    # 转换 HTML 到 Markdown
    markdown_content = h.handle(html_content)
    return markdown_content


class ParserTools:

    def __init__(self):
        self.table_engine = PPStructure(layout=False, show_log=True)
        # 初始化 PaddleOCR
        self.ocr = PaddleOCR()  # 自动语言检测可以设置为默认

    def do_parse_pdf(self, pdf_path):
        """
        解析 PDF
        :param pdf_path:
        :return:
        """
        pdf_data = read_fn(pdf_path)
        jso = []
        pdf_file_name = Path(pdf_path).stem
        # method = 'ocr'
        method = 'auto'
        # parse_pdf_methods = click.Choice(["ocr", "txt", "auto"])
        magicpdf.model_config.__use_inside_model__ = True
        magicpdf.model_config.__model_mode__ = "full"
        magicpdf.do_parse(
            pdf_file_name,
            pdf_data,
            jso,
            method,
        )
        print(pdf_file_name)
        parsed_pdf_path = os.path.join('tmp', 'magic-pdf', pdf_file_name, method, f'{pdf_file_name}.md')
        parsed_pdf_root = os.path.join('tmp', 'magic-pdf', pdf_file_name, method)
        return parsed_pdf_root, parsed_pdf_path, pdf_file_name

    def ocr_table(self, img_path, is_debug=False, convert_md=False):
        """
        解析图片 ocr 表格
        :param img_path:
        :param is_debug:
        :param convert_md:
        :return:
        """
        save_folder = './output'
        img = cv2.imread(img_path)
        result = self.table_engine(img)
        if is_debug:
            save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])
        for line in result:
            # print(line)
            content = line['res']['html']
            if convert_md:
                # 转换 HTML 到 Markdown
                content = html_to_markdown(content).replace('#', ' ')
                # 输出转换后的 Markdown 内容
            print(content)
            return content

    def ocr_image(self, img_path):
        """
        解析图片 ocr
        :param img_path:
        :return:
        """
        # 执行 OCR
        result = self.ocr.ocr(img_path)
        # print(result)
        # 提取识别到的文本
        extracted_texts = [line_txt[1][0]
                           for line in result
                               for line_txt in line
                           ]
        # print(extracted_texts)
        return extracted_texts

    def parserPDF(self, pdf_path, parsed_pdf_path_result):
        """
        解析 PDF
        :param pdf_path:
        :param parsed_pdf_path_result:
        :return:
        """
        parsed_pdf_root, parsed_pdf_path, pdf_file_name = self.do_parse_pdf(pdf_path=pdf_path)
        # print(parsed_pdf_root, parsed_pdf_path, pdf_file_name)

        content_list_path = os.path.join(parsed_pdf_root, f'{pdf_file_name}_content_list.json')
        with open(content_list_path, 'r', encoding='utf-8') as f:
            content_list = json.load(f)

        content_dict = {
            'table': [],
            'image': [],
        }
        for i in content_list:
            if i['type'] == 'table':
                content_dict['table'].append(i['img_path'])
                content_dict[i['img_path']] = i.get('table_caption', '')
            elif i['type'] == 'image':
                content_dict['image'].append(i['img_path'])
                content_dict[i['img_path']] = i.get('img_caption', '')

        all_content = ''
        with open(parsed_pdf_path, 'r', encoding='utf-8') as f, open(parsed_pdf_path_result, 'w',
                                                                     encoding='utf-8') as f2:
            line = f.readline()
            while line:
                all_content += line
                if line.startswith('![](images'):
                    print(line)
                    key = line.replace('![](', '').replace(')', '').strip()
                    img_path = os.path.join(parsed_pdf_root, key)
                    if key in content_dict['table']:
                        result = self.ocr_table(img_path)
                        print(result)
                    else:
                        result = self.ocr_image(img_path)
                        result = ' '.join(result)
                        print(result)

                    if content_dict.get(key) and content_dict.get(key) not in all_content:
                        result = content_dict.get(key) + '\n' + result
                        f2.write(result + '\n')
                    else:
                        f2.write(result + '\n')

                else:
                    f2.write(line + '\n')

                line = f.readline()


if __name__ == '__main__':
    parser = ParserTools()
    # 图片路径
    # img_path = 'images2/dfbdf7600b058ed84ae39235f92b516bb7a68534dd5bb9f09a4389deb5cbcfa9.jpg'
    # img_path = 'images2/ff589eaa9a94eb86226279fa1bef181d5813bfe9a5380317c3475215441d03e7.jpg'
    # result = parser.ocr_image(img_path)
    # print(result)
    pdf_path = 'LKV312-V2.0中文说明书.pdf'
    parsed_pdf_path_result = 'LKV312-V2.0中文说明书parsed_pdf_2.md'
    parser.parserPDF(pdf_path, parsed_pdf_path_result)

    def test():
        parsed_pdf_root, parsed_pdf_path, pdf_file_name = parser.do_parse_pdf(pdf_path=pdf_path)
        print(parsed_pdf_root, parsed_pdf_path, pdf_file_name)
        # parsed_pdf_root = 'tmp/magic-pdf/LKV312-V2.0中文说明书/auto/'
        # parsed_pdf_path = 'tmp/magic-pdf/LKV312-V2.0中文说明书/auto/LKV312-V2.0中文说明书.md'
        # content_list_path = 'tmp/magic-pdf/LKV312-V2.0中文说明书/auto/LKV312-V2.0中文说明书_content_list.json'
        content_list_path = os.path.join(parsed_pdf_root, f'{pdf_file_name}_content_list.json')

        with open(content_list_path, 'r', encoding='utf-8') as f:
            content_list = json.load(f)

        content_dict = {
            'table': [],
            'image': [],
        }
        for i in content_list:
            if i['type'] == 'table':
                content_dict['table'].append(i['img_path'])
                content_dict[i['img_path']] = i.get('table_caption', '')
            elif i['type'] == 'image':
                content_dict['image'].append(i['img_path'])
                content_dict[i['img_path']] = i.get('img_caption', '')

        all_content = ''
        with open(parsed_pdf_path, 'r', encoding='utf-8') as f, open(parsed_pdf_path_result, 'w', encoding='utf-8') as f2:
            line = f.readline()
            while line:
                all_content += line
                if line.startswith('![](images'):
                    print(line)
                    key = line.replace('![](', '').replace(')', '').strip()
                    img_path = os.path.join(parsed_pdf_root, key)
                    if key in content_dict['table']:
                        result = parser.ocr_table(img_path)
                        print(result)
                    else:
                        result = parser.ocr_image(img_path)
                        result = ' '.join(result)
                        print(result)

                    if content_dict.get(key) and content_dict.get(key) not in all_content:
                        result = content_dict.get(key) + '\n' + result
                        f2.write(result + '\n')
                    else:
                        f2.write(result + '\n')

                else:
                    f2.write(line + '\n')

                line = f.readline()



