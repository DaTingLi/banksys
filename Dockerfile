# 银行认购在线预测服务运行镜像(只装运行依赖,保持精简)
FROM python:3.11-slim

WORKDIR /app

# 支持通过构建参数切换 pip 镜像源:国内服务器用清华源更快。
ARG PIP_INDEX_URL=https://pypi.org/simple

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 拷贝源码与已训练好的模型(models/model.pkl 需在构建前生成)
COPY src ./src
COPY models ./models

EXPOSE 8000

# 用 gunicorn + uvicorn worker 起 FastAPI,生产更稳。
CMD ["gunicorn", "src.prediction_service.service:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000"]
