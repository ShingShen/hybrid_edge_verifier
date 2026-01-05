# Hybrid Egde Verifier

## Build Python Virtual Environment
```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Build Docker Images
```
sudo docker build -t hybrid_edge_verifier .
```

## SSH Connection
```
sudo python3 main.py --device device_a --conn ssh
```

## Binding Rust to Python
1. Go to the folder which has Cargo.toml
2. Input the command
    ```
    maturin develop
    ```