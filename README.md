# 使用MinU magic-pdf paddleocr, 进行数据处理 pdf
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