# xsr3_recontruct
Tool for reconstruction of Samsung XSR3 Flash Transaction Layer

## Usage

1. Convert onenand.bin and onenand.oob to flash.bin

```bash
onenand2flash.py
```

2. Extract fat from flash.bin and reconstruct xsr3
```bash
de_xsr3.py flash.bin output_directory
```
