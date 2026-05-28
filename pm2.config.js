module.exports = {
    apps: [
        {
            name: "ileva-ocr",
            script: "./venv/bin/uvicorn",
            args: "app.main:app --host 0.0.0.0 --port 5500 --workers 2",
            interpreter: "none",
            cwd: __dirname,
            env: {
                PYTHONUNBUFFERED: "1",
            },
            restart_delay: 3000,
            max_restarts: 10,
            log_date_format: "YYYY-MM-DD HH:mm:ss",
        },
    ],
};
