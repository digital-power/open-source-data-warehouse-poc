FROM apache/airflow:3.0.2-python3.11 as builder

###########################
######## Install UV #######
###########################

# Switch to root user
USER root

# Install curl, ca-certificates, and UV in a single layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -sSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
ENV PATH="/root/.cargo/bin:$PATH"

###########################
######## Copy src #########
###########################

# Create app directory and copy source files
RUN mkdir -p ${AIRFLOW_HOME}/app/src

# Copy files in separate commands to avoid the path not found error
COPY ./pyproject.toml ./uv.lock ./README.md ./.python-version ${AIRFLOW_HOME}/app/
COPY ./src/ ${AIRFLOW_HOME}/app/src/
COPY ./dbt/ ${AIRFLOW_HOME}/app/dbt/

###############################
#### Install dependencies #####
###############################

# Install dependencies using uv sync with the lock file
WORKDIR ${AIRFLOW_HOME}/app
RUN uv sync && \
    # Create symlinks for CLI tools to make them available in PATH
    ln -sf ${AIRFLOW_HOME}/app/.venv/bin/dbt /usr/local/bin/dbt && \
    rm -rf ~/.cache/uv ~/.cache/pip

# Create a smaller final image
FROM apache/airflow:3.0.2-python3.11

# Copy only the installed packages and application code
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder ${AIRFLOW_HOME}/app/ ${AIRFLOW_HOME}/app/
COPY --from=builder /usr/local/bin/dbt /usr/local/bin/dbt

# Copy the DAGs directory
COPY ./dags/ ${AIRFLOW_HOME}/dags/

# Permissions for airflow user
USER root
RUN chown -R airflow:root ${AIRFLOW_HOME}/app && \
    chmod -R 755 ${AIRFLOW_HOME}/app && \
    mkdir -p ${AIRFLOW_HOME}/app/dbt/logs && \
    chown -R airflow:root ${AIRFLOW_HOME}/app/dbt/logs && \
    chmod -R 777 ${AIRFLOW_HOME}/app/dbt/logs

# Switch back to airflow user
USER airflow

# Add app directory to PYTHONPATH so Python can find the modules
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}/app"

# Set working directory
WORKDIR ${AIRFLOW_HOME}
