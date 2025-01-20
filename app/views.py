from django.shortcuts import render
import json
from django.http import JsonResponse
import numpy as np
import math
import re

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
    code = code.replace('}', '')  # Remove chaves de fechamento
    code = re.sub(r';\s*$', '', code, flags=re.MULTILINE)
    return code

def exec_code(code, pixels):
    exec(
        code,
        {
            'fillScreen': lambda color: fill_screen(color, pixels),
            'drawLine': lambda x1, y1, x2, y2, color: draw_line(x1, y1, x2, y2, color, pixels),
            'fillCircle': lambda x, y, r, color: fill_circle(x, y, r, color, pixels),
            'drawCircle': lambda x, y, r, color: draw_circle(x, y, r, color, pixels),
            'fillRect': lambda x, y, width, height, color: fill_rect(x, y, width, height, color, pixels),
            'drawRect': lambda x, y, width, height, color: draw_rect(x, y, width, height, color, pixels),
            'fillTriangle': lambda x1, y1, x2, y2, x3, y3, color: fill_triangle(x1, y1, x2, y2, x3, y3, color, pixels),
            'drawTriangle': lambda x1, y1, x2, y2, x3, y3, color: draw_triangle(x1, y1, x2, y2, x3, y3, color, pixels),
            'pixels': pixels,
            'GxEPD_BLACK': GxEPD_BLACK,
            'GxEPD_WHITE': GxEPD_WHITE,
            'range': range
        },
    )
    

def draw_fast_vline(x, y, h, color, pixels):
    draw_line(x, y, x, y+h-1, color, pixels)
    
def draw_fast_hline(x, y, w, color, pixels):
    draw_line(x, y, x+w-1, y, color, pixels)

def fill_screen(color, pixels):
    pixels.fill(color)      
    
def draw_line(x0, y0, x1, y1, color, pixels):
    steep = abs(y1 - y0) > abs(x1 - x0)
    
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        
    dx = x1 - x0
    dy = abs(y1 - y0)
    
    err = dx/2
    
    if y0 < y1:
        ysteep = 1
    else:
        ysteep = -1
        
    while x0 <= x1:
        if steep:
            pixels[x0][y0] = color
        else:
            pixels[y0][x0] = color
        err-=dy
        if err < 0:
            y0 += ysteep
            err += dx
        x0+=1
        
    

def fill_circle(x0, y0, r, color, pixels):
    draw_fast_vline(x0, y0-r, 2*r+1, color, pixels)
    
    f = 1-r
    ddF_x = 1
    ddF_y = -2*r
    x = 0
    y = r
    px = x
    py = y
    
    delta = 1
    corners = 3
    
    while x < y:
        if f >= 0:
            y-=1
            ddF_y += 2
            f += ddF_y
            
        x+=1
        ddF_x += 2
        f += ddF_x
        
        if x < (y+1):
            if corners & 1:
                draw_fast_vline(x0 + x, y0 - y, 2 * y + delta, color, pixels)
            if corners & 2:
                draw_fast_vline(x0 - x, y0 - y, 2 * y + delta, color, pixels)
                
        if y!=py:
            if corners & 1:
                draw_fast_vline(x0 + py, y0 - px, 2 * px + delta, color, pixels)
            if corners & 2:
                draw_fast_vline(x0 - py, y0 - px, 2 * px + delta, color, pixels)
            py=y
        px = x            
                

def draw_circle(x0, y0, r, color, pixels):
    f = 1-r
    ddF_x = 1
    ddF_y = -2*r
    x = 0
    y = r
    
    pixels[y0+r][x0] = color
    pixels[y0-r][x0] = color
    pixels[y0][x0+r] = color
    pixels[y0][x0-r] = color
    
    while x < y:
        if f >= 0:
            y-=1
            ddF_y += 2
            f += ddF_y
        
        x+=1
        ddF_x += 2
        f += ddF_x
        
        pixels[y0 + y][x0 + x] = color
        pixels[y0 + y][x0 - x] = color
        pixels[y0 - y][x0 + x] = color
        pixels[y0 - y][x0 - x] = color
        pixels[y0 + x][x0 + y] = color
        pixels[y0 + x][x0 - y] = color
        pixels[y0 - x][x0 + y] = color
        pixels[y0 - x][x0 - y] = color
    

def fill_rect(x, y, w, h, color, pixels):
    for i in range(x, x+w):
        draw_fast_vline(i, y, h, color, pixels)

def draw_rect(x, y, w, h, color, pixels):
    draw_fast_hline(x, y, w, color, pixels)  
    draw_fast_hline(x, y + h - 1, w, color, pixels) 
    draw_fast_vline(x, y, h, color, pixels) 
    draw_fast_vline(x + w - 1, y, h, color, pixels) 

def fill_triangle(x0, y0, x1, y1, x2, y2, color, pixels):
    if y0 > y1:
        y0, y1 = y1, y0
        x0, x1 = x1, x0
    if y1 > y2:
        y1, y2 = y2, y1
        x1, x2 = x2, x1
    if y0 > y1:
        y0, y1 = y1, y0
        x0, x1 = x1, x0
        
    if y0 == y2:
        a = b = x0
        if x1 < a:
            a = x1
        elif x1 > b:
            b = x1
        if x2 < a:
            a = x2
        elif x2 > b:
            b = x2
        draw_fast_hline(a, y0, b - a + 1, color, pixels)
        return
    
    dx01 = x1 - x0
    dy01 = y1 - y0
    dx02 = x2 - x0
    dy02 = y2 - y0
    dx12 = x2 - x1
    dy12 = y2 - y1
    sa = 0
    sb = 0
    
    if y1 == y2:
        last = y1
    else:
        last = y1 - 1
        
    for y in range(y0, last+1):
        a = x0 + sa // dy01
        b = x0 + sb // dy02
        sa += dx01
        sb += dx02
        if a > b:
            a, b = b, a
        draw_fast_hline(a, y, b - a + 1, color, pixels)
        
    y = last
    sa = int(dx12) * (y - y1)
    sb = int(dx02) * (y - y0)
    for y in range(y1, y2+1):
        a = x1 + sa // dy12
        b = x0 + sb // dy02
        sa += dx12
        sb += dx02
        if a > b:
            a, b = b, a
        draw_fast_hline(a, y, b - a + 1, color, pixels)

def draw_triangle(x0, y0, x1, y1, x2, y2, color, pixels):
    draw_line(x0, y0, x1, y1, color, pixels)
    draw_line(x1, y1, x2, y2, color, pixels)
    draw_line(x2, y2, x0, y0, color, pixels)