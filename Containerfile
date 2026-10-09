# spm-python and JupyterLab in a container:
#   Debian's Python 3.13 in a venv with packages pinned from requirements.txt
#   plus only the five MATLAB Runtime R2025b products that SPM needs.
#
# Starts JupyterLab by default and GUI figures appear on the host's display
# if one is provided otherwise the MATLAB Runtime draws them on its own virtual display.
#
# Build the image from the root of this repository:
#   podman build --file Containerfile --tag spm-python-setup .
#   docker build --file Containerfile --tag spm-python-setup .
#
# The build runs MathWorks' installer, which needs the MATLAB Runtime licence
# to be accepted (AGREE_TO_MATLAB_RUNTIME_LICENSE=yes is the default).

FROM docker.io/library/debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f

LABEL org.opencontainers.image.source="https://github.com/pranaysy/spm-python-setup"

ARG AGREE_TO_MATLAB_RUNTIME_LICENSE=yes

# Set up system packages and environment
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-venv ca-certificates tini \
      libxfont2 libtirpc3t64 xkb-data x11-xkb-utils \
      libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 \
      libcups2t64 libdrm2 libfontconfig1 libfreetype6 libgbm1 \
      libgdk-pixbuf-2.0-0 libgl1 libgtk2.0-0t64 libice6 libnspr4 libnss3 \
      libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxt6t64 libxtst6 \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix # for display

# spm-python and JupyterLab in  venv
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/spm-venv \
 && /opt/spm-venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Set env variables for MATLAB Runtime
ENV MATLAB_RUNTIME_PATH=/opt/MATLAB/MATLAB_Runtime \
    LD_LIBRARY_PATH=/opt/MATLAB/MATLAB_Runtime/R2025b/bin/glnxa64 \
    PATH=/opt/spm-venv/bin:$PATH

# Selective installation of only those runtime products that SPM's compiled
# package declares in its buildresult.json
COPY install_runtime_products.py /tmp/install_runtime_products.py
RUN mkdir -p /var/tmp/mcr \
 && TMPDIR=/var/tmp/mcr \
    AGREE_TO_MATLAB_RUNTIME_LICENSE="$AGREE_TO_MATLAB_RUNTIME_LICENSE" \
    python /tmp/install_runtime_products.py \
 && rm -rf /var/tmp/mcr /tmp/install_runtime_products.py

EXPOSE 8888

RUN useradd --create-home --uid 1000 spm
USER spm
WORKDIR /home/spm
ENTRYPOINT ["tini", "--"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
