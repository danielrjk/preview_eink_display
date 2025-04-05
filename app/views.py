from django.shortcuts import render
import json
from django.http import JsonResponse
import numpy as np
import math
import re
from bdfparser import Font
import os

# CLASSES CUSTOMIZADAS
from .classes import Tela, Fontes, BarCode


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
            print(str(e))
            return JsonResponse({'error': str(e)}, status=400)

def convert_c_to_python(code):
    
    code = re.sub(
        r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+);\s*\1\s*<\s*(\d+);\s*\1\+\+\s*\)\s*\{',
        r'for \1 in range(\2, \3):',
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
    code = re.sub(r';\s*$', '', code, flags=re.MULTILINE)
    
    return code

def exec_code(code, pixels):
    tela = Tela(pixels)
    fontes = Fontes(tela)
    barcode = BarCode(tela)
    exec(
        code,
        {
            'tela': tela,
            'fontes': fontes,
            'barcode': barcode,
            'pixels': pixels,
            'GxEPD_BLACK': GxEPD_BLACK,
            'GxEPD_WHITE': GxEPD_WHITE,
            'range': range,
        },
    )
  
