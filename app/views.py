from django.shortcuts import render
import json
from django.http import JsonResponse, Http404
import numpy as np
import math
import re
from bdfparser import Font
import os
import traceback

# CLASSES CUSTOMIZADAS
from .classes import Tela, Fontes, BarCode, BarcodeType, QRCode

# CONSTANTES
GxEPD_BLACK = 1
GxEPD_WHITE = 0

def visualizador(request):
    return render(request, 'visualizador.html')

def process_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        rotacao = data.get('rotacao', '')
        width, height = (296, 128) if rotacao in [1, 3] else (128, 296)
        pixels = np.full((height, width), GxEPD_WHITE)  
        
        code = convert_c_to_python(code)

        try:
            exec_code(code, pixels)
            return JsonResponse({'pixels': pixels.tolist()})
        except Exception as e:
            d = str(e).split("-")
            if len(d) == 2:
                line_num = d[1]
            else:
                line_num = 0
            return JsonResponse({'error': d[0], 'line': line_num}, status=400)
    else:
        return Http404

def _convert_for_loop(match):
    var = match.group(1)
    start = match.group(2)
    op = match.group(3)
    end = match.group(4)
    increment = match.group(5).strip()

    if increment in (f'{var}++', f'++{var}'):
        if op == '<':
            return f'for {var} in range({start}, {end}):'
        elif op == '<=':
            return f'for {var} in range({start}, {end}+1):'
    elif increment in (f'{var}--', f'--{var}'):
        if op == '>':
            return f'for {var} in range({start}, {end}, -1):'
        elif op == '>=':
            return f'for {var} in range({start}, {end}-1, -1):'
    else:
        step_match = re.match(rf'{re.escape(var)}\s*(\+|-)\s*=\s*(\w+)', increment)
        if step_match:
            sign = step_match.group(1)
            step = step_match.group(2)
            if sign == '+':
                if op == '<':
                    return f'for {var} in range({start}, {end}, {step}):'
                elif op == '<=':
                    return f'for {var} in range({start}, {end}+1, {step}):'
            elif sign == '-':
                if op == '>':
                    return f'for {var} in range({start}, {end}, -{step}):'
                elif op == '>=':
                    return f'for {var} in range({start}, {end}-1, -{step}):'

    return match.group(0)

def convert_c_to_python(code):
    code = re.sub(
        r'for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*(\w+)\s*;\s*\1\s*(<=?|>=?)\s*(\w+)\s*;\s*((?:\1\+\+|\+\+\1|\1--|\-\-\1|\1\s*[\+\-]=\s*\w+))\s*\)\s*\{',
        _convert_for_loop,
        code
    )
    
    code = re.sub(
        r'(fontes\.setFont\()\s*(\w+)\s*(\);)',
        r'\1"\2"\3',
        code
    )
    
    code = re.sub(
        r'(fontes\.drawGlyph\()\s*(\w+)\s*(,.*\);)', 
        r'\1"\2"\3', 
        code
    )
    
    
    # ULTIMOS
    code = code.replace('}', '')  # Remove chaves de fechamento
    code = code.replace('true', 'True')
    code = code.replace('false', 'False')
    code = re.sub(r';[^\S\n]*$', '', code, flags=re.MULTILINE)

    lines = code.split("\n")
    code = "\n".join(linha.rstrip() for linha in lines)

    
    return code

def exec_code(code, pixels):
    tela = Tela(pixels)
    fontes = Fontes(tela)
    barcode = BarCode(tela)
    qrcode = QRCode(tela)
    try:
        compiled_code = compile(code, '<user-code>', 'exec')
        exec(
            compiled_code,
            {
                'tela': tela,
                'display': tela,
                'fontes': fontes,
                'fonts': fontes,
                'barcode': barcode,
                'codigoBarras': barcode,
                'qrcode': qrcode,
                'qr': qrcode,
                'pixels': pixels,
                'GxEPD_BLACK': GxEPD_BLACK,
                'GxEPD_WHITE': GxEPD_WHITE,
                'range': range,
                'EAN13': BarcodeType.EAN13,
                'EAN8': BarcodeType.EAN8,
                'UPCA': BarcodeType.UPCA,
                'UPCE': BarcodeType.UPCE,
            },
        )
    except SyntaxError as e:
        raise Exception(f"Erro de sintaxe na linha {e.lineno}: {e.msg} -{e.lineno}")
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        error_line = None
        for frame in tb:
            if frame.filename == '<user-code>':
                error_line = frame.lineno
                break
        if error_line is None:
            error_line = 'desconhecida'
            raise Exception(f"Erro: {str(e)}")
        raise Exception(f"Erro na linha {error_line}: {str(e)} -{error_line}")
  
