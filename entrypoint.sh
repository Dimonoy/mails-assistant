#/bin/sh

LOCAL=${LOCAL:-false}
export $(grep -v '^#' .env | xargs)

if [ ! -e $DATA_PATH ] && [ $LOCAL = true ]; then
    echo "Please setup the DATA_PATH:"
    echo "> sudo mkdir -p $DATA_PATH"
    echo "> sudo chown -R 1000:1000 $DATA_PATH"
    exit 1
fi

if [ $LOCAL = false ]; then
    mkdir -p $DATA_PATH
    chown -R 1000:1000 $DATA_PATH
fi

cp -r data/* $DATA_PATH
mkdir -p $DATA_PATH/$GOOGLE_TOKENS_DIR

if [ ! -e "$DATA_PATH/$LLM_INSTRUCTIONS_FILE" ]; then
    echo "Instructions file is abscent. Generating empty instructions."
    touch "$DATA_PATH/$LLM_INSTRUCTIONS_FILE"
fi

fastapi dev mails_assistant/main.py
