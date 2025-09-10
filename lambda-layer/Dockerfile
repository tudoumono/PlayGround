FROM public.ecr.aws/lambda/python:3.12

# 作業ディレクトリを設定
WORKDIR /opt

# requirements.txtをコピー
COPY requirements.txt .

# Python依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt -t python/

# python/ディレクトリの内容を確認
RUN ls -la python/

# lxmlのテスト
RUN python -c "import sys; sys.path.insert(0, 'python'); from lxml import etree; print('✅ lxml etree import successful in Lambda container')"