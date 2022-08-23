FROM tensorflow/tensorflow:1.15.5-gpu-py3

# https://github.com/NVIDIA/nvidia-docker/issues/1632#issuecomment-1112667716
RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list

# https://serverfault.com/a/992421
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get update && apt-get install -y \
    cmake \
    zlib1g-dev \
    libzip-dev \
    nvidia-opencl-dev \
    jupyter-notebook

ENV PATH /opt/conda/bin:$PATH

# notebook port
EXPOSE 8888
# visdom port
EXPOSE 8097

# Set up our notebook config.
COPY ./docker/jupyter_notebook_config.py /root/.jupyter/
 
# Jupyter has issues with being run directly:
#   https://github.com/ipython/ipython/issues/7062
# We just add a little wrapper script.
COPY ./docker/run_jupyter.sh /
RUN chmod +x /run_jupyter.sh
 
CMD ["/run_jupyter.sh", "--allow-root"]

