# 使用官方Python镜像作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器的工作目录中
COPY ./ .

# 安装requirements.txt中指定的任何所需包
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV AUTO_HALCYON_ENV=DOCKER

# 使用cron作为定时器
# 安装cron并设置定时任务
RUN apt-get update && apt-get -y install cron
RUN chmod 777 /var/run
RUN printenv > /etc/environment

COPY ./docker/crontab /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/my-cron-job

# 让cron在前台运行
CMD cron && tail -f /var/log/cron.log
# CMD ["python", "main.py"]


# docker build -t auto-halcyon -f docker/Dockerfile .
# docker run -d --name auto_halcyon --restart always --user $(id -u):$(id -g) -v $(pwd)/.localconfig.yaml:/app/.localconfig.yaml auto-halcyon:latest

# docker run -d --name auto_halcyon auto-halcyon:latest

