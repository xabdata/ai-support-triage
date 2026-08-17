FROM anaconda/miniconda:26.5.3

ENV CONDA_PLUGINS_AUTO_ACCEPT_TOS=true

WORKDIR /app

COPY environment.yml .

RUN conda env create -f environment.yml \
    && conda clean --all --yes

ENV PATH="/opt/miniconda3/envs/ai_support_triage/bin:$PATH"

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
