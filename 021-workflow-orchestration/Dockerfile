FROM apache/airflow:2.8.1
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         wget \
         gzip \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir \
    apache-airflow-providers-google==10.10.0 \
    apache-airflow-providers-postgres==5.7.1
