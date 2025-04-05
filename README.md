# Zonaprop - Herramienta de Extracción de Datos

Esta aplicación facilita la extracción y procesamiento de datos de propiedades inmobiliarias de Zonaprop.

## Descripción

Este proyecto consiste en una serie de scripts de Python diseñados para automatizar la recolección y procesamiento de datos de propiedades inmobiliarias de Zonaprop (portal inmobiliario de Argentina). Cada script cumple una función específica en el proceso de extracción y manipulación de datos.

## Componentes del Proyecto

1. **autoclick_extraer_enlaces.py**: Herramienta de auto-clicker para extraer enlaces de propiedades.
   
2. **unir_propiedades_individuales.py**: Script para combinar datos de propiedades individuales.
   
3. **abrir_links.py**: Abre enlaces de propiedades desde archivos CSV en lotes configurables.
   
4. **autoclick_propiedades.py**: Auto-clicker para páginas de propiedades específicas.
   
5. **unir_propiedades_csv.py**: Combina datos de propiedades de varios archivos CSV.
   
6. **aplicar_filtros.py**: Aplica filtros específicos a los datos recolectados.

## Requisitos

- Python 3.x
- Pandas
- PyAutoGUI
- Tkinter

## Uso

Cada script debe ejecutarse en orden, siguiendo el flujo de trabajo:

1. Extraer enlaces de propiedades
2. Unir propiedades individuales
3. Abrir los enlaces
4. Extraer datos de cada propiedad
5. Unir todos los datos en un CSV
6. Aplicar filtros específicos

## Notas

- Los scripts incluyen interfaces gráficas para facilitar su uso
- Es posible configurar parámetros como retrasos entre clics, número de iteraciones, etc. 