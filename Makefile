# Caminho para a aplicação
APP_DIR=$(shell pwd)

# PID file
PID_FILE=$(shell pwd)/transferencia.pid

# Out file
OUT_FILE=$(shell pwd)/out.log

# Comando para iniciar o Python
PYTHON_CMD=nohup python3 -u app.py >> $(OUT_FILE)

.PHONY: start stop status

start:
	@echo "Iniciando a aplicação..."
	@cd $(APP_DIR) && ( $(PYTHON_CMD) & echo $$! > $(PID_FILE) )
	@echo "Aplicação iniciada."

stop:
	@echo "Parando a aplicação..."
	@if [ -f $(PID_FILE) ]; then \
		kill `cat $(PID_FILE)`; \
		rm $(PID_FILE); \
		echo "Aplicação parada."; \
	else \
		echo "PID file não encontrado. A aplicação pode não estar em execução."; \
	fi

status:
	@echo "Verificando status da aplicação..."
	@if [ -f "$(PID_FILE)" ]; then \
	    if ps -p $$(cat $(PID_FILE)) > /dev/null; then \
	        echo "Aplicação está em execução."; \
	        echo "PID: $$(cat $(PID_FILE))"; \
	    else \
	        echo "Aplicação não está em execução."; \
	    fi; \
	else \
	    echo "Arquivo PID não encontrado."; \
	fi
