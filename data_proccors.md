


# 使用MinU, 进行数据处理 pdf
conda create -n MinerU2 python=3.10
conda activate MinerU2
pip install magic-pdf
pip install detectron2 --extra-index-url https://myhloli.github.io/wheels/
pip install magic-pdf[full-cpu]
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install "paddleocr>=2.6.0.3"  -i https://mirror.baidu.com/pypi/simple
pip install html2text  -i https://mirror.baidu.com/pypi/simple

安装完测试看看：
magic-pdf pdf-command --pdf "3060中文.pdf" --inside_model true
paddleocr --image_dir=test.jpg --type=structure --layout=false


# 使用MinU, 进行数据处理 docx
conda create -n magicdoc python=3.10
conda activate magicdoc
安装 libreoffice 
添加 "install_dir\LibreOffice\program" to 环境变量 PATH
C:\Program Files\LibreOffice\program
pip install fairy-doc[cpu] 
https://github.com/InternLM/magic-doc/blob/main/README_zh-CN.md








