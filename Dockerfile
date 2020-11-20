ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

RUN pip install --upgrade pip setuptools

WORKDIR /opt/wagyu

COPY requirements-setup.txt .
RUN pip install --force-reinstall -r requirements-setup.txt

COPY requirements.txt .
RUN pip install --force-reinstall -r requirements.txt

COPY requirements-tests.txt .
RUN pip install --force-reinstall -r requirements-tests.txt

COPY README.md .
COPY pytest.ini .
COPY setup.py .
COPY include/ include/
COPY src/ src/
COPY wagyu/ wagyu/
COPY tests/ tests/

RUN pip install -e .
