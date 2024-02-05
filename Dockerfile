FROM rocker/r-ver:4.3.2

WORKDIR /project

RUN /rocker_scripts/install_python.sh

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y git 
RUN apt-get install -y pipx
RUN pipx ensurepath

# https://github.com/pypa/pipx/issues/754
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install git+https://github.com/splor-mg/dpm.git

COPY requirements.txt .
COPY DESCRIPTION .

RUN python3 -m pip install -r requirements.txt
RUN Rscript -e "install.packages('renv')"
RUN Rscript -e "install.packages('dotenv')" 
RUN --mount=type=secret,id=secret Rscript -e "dotenv::load_dot_env('/run/secrets/secret'); renv::install()"
