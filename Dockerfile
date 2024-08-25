FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml .

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "nadeulAI-SSE", "/bin/bash", "-c"]

COPY . /app

RUN pip install --no-cache-dir -e .

CMD ["uvicorn", "nadeulAI_SSE.test.test:app", "--host=0.0.0.0", "--port=8000", "--reload"]

