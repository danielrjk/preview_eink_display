from django.shortcuts import render
import json
from django.http import JsonResponse
import numpy as np
import math

# CONSTANTES
GxEPD_BLACK = 1
GxEPD_WHITE = 0

def visualizador(request):
    return render(request, 'visualizador.html')

def process_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        width, height = 296, 128
        pixels = np.full((height, width), GxEPD_WHITE)  # Matriz preenchida com branco

        try:
            exec_code(code, pixels)
            return JsonResponse({'pixels': pixels.tolist()})
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': str(e)}, status=400)

def exec_code(code, pixels):
    exec(
        code,
        {
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
        },
    )

def draw_line(x1, y1, x2, y2, color, pixels):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if 0 <= y1 < pixels.shape[0] and 0 <= x1 < pixels.shape[1]:
            pixels[y1][x1] = color
        
        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def fill_circle(x, y, r, color, pixels):
    for i in range(x - r, x + r + 1):
        for j in range(y - r, y + r + 1):
            if 0 <= j < pixels.shape[0] and 0 <= i < pixels.shape[1]:
                if (i - x) ** 2 + (j - y) ** 2 <= r ** 2:
                    pixels[j][i] = color

def draw_circle(x, y, r, color, pixels):
    for i in range(x - r, x + r + 1):
        for j in range(y - r, y + r + 1):
            if 0 <= j < pixels.shape[0] and 0 <= i < pixels.shape[1]:
                if r - 1 <= math.sqrt((i - x) ** 2 + (j - y) ** 2) <= r + 1:
                    pixels[j][i] = color

def fill_rect(x, y, width, height, color, pixels):
    for i in range(x, x + width):
        for j in range(y, y + height):
            if 0 <= j < pixels.shape[0] and 0 <= i < pixels.shape[1]:
                pixels[j][i] = color

def draw_rect(x, y, width, height, color, pixels):
    draw_line(x, y, x + width, y, color, pixels) 
    draw_line(x, y, x, y + height, color, pixels)  
    draw_line(x + width, y, x + width, y + height, color, pixels)  
    draw_line(x, y + height, x + width, y + height, color, pixels)  

def fill_triangle(x1, y1, x2, y2, x3, y3, color, pixels):
    def edge_interpolate(y, x1, y1, x2, y2):
        if y1 == y2:
            return x1
        return x1 + (x2 - x1) * (y - y1) / (y2 - y1)

    ymin = min(y1, y2, y3)
    ymax = max(y1, y2, y3)

    for y in range(ymin, ymax + 1):
        x_left = min(
            edge_interpolate(y, x1, y1, x2, y2),
            edge_interpolate(y, x1, y1, x3, y3),
            edge_interpolate(y, x2, y2, x3, y3),
        )
        x_right = max(
            edge_interpolate(y, x1, y1, x2, y2),
            edge_interpolate(y, x1, y1, x3, y3),
            edge_interpolate(y, x2, y2, x3, y3),
        )

        for x in range(math.floor(x_left), math.ceil(x_right) + 1):
            if 0 <= y < pixels.shape[0] and 0 <= x < pixels.shape[1]:
                pixels[y][x] = color

def draw_triangle(x1, y1, x2, y2, x3, y3, color, pixels):
    draw_line(x1, y1, x2, y2, color, pixels)
    draw_line(x2, y2, x3, y3, color, pixels)
    draw_line(x3, y3, x1, y1, color, pixels)