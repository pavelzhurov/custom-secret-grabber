FROM docker.io/python:slim
COPY grabber.py requirements.txt /app/
RUN python -m pip install -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["grabber.py"]
