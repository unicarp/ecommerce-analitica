# 📊 E-Commerce Strategic Analytics Suite

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/ML-KMeans-orange?style=for-the-badge&logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Viz-Plotly-3F4F75?style=for-the-badge&logo=plotly)

## ✒️ Autores

* **Anotnio Eugenio Daniel** - *Desarrollo del Pipeline ETL*
* **Domínguez Espinoza Juan Pablo** - *Modelado K-Means y Dashboard Interactivo*

---
*Proyecto desarrollado como evaluación final para la asignatura de Analítica y Visualización de Datos.*

## 📖 Descripción del Proyecto

Este proyecto es una solución integral de **Inteligencia de Negocios (BI) y Ciencia de Datos** diseñada para analizar transacciones de E-Commerce y generar estrategias comerciales basadas en evidencia.

Utilizando una **arquitectura desacoplada**, el sistema procesa datos crudos mediante un pipeline ETL en Jupyter Notebooks y despliega los resultados en una aplicación web interactiva desarrollada con Streamlit. El objetivo es responder preguntas críticas de negocio sobre segmentación de clientes, ciclos de venta y expansión geográfica.

---

## 🎯 Objetivos y Alcance

1.  **Diagnóstico de Datos:** Auditoría de calidad y limpieza de registros transaccionales (eliminación de devoluciones y nulos).
2.  **Detección de Patrones (Fourier):** Validación matemática de ciclos de estacionalidad mediante Transformada de Fourier (FFT).
3.  **Segmentación de Clientes (Clustering):** Agrupamiento de usuarios mediante algoritmo K-Means basado en comportamiento RFM (Recencia, Frecuencia, Monto).
4.  **Estrategia Geográfica:** Identificación de mercados saturados y oportunidades de expansión internacional.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python
* **Procesamiento de Datos:** Pandas, NumPy
* **Machine Learning:** Scikit-learn (K-Means, StandardScaler)
* **Matemáticas Avanzadas:** Scipy (fftpack para análisis espectral)
* **Visualización:** Plotly Express, Plotly Graph Objects
* **Frontend / Dashboard:** Streamlit

---

## 🧠 Metodología Analítica

### 1. Preprocesamiento (ETL)
* Limpieza de facturas con prefijo 'C' (Cancelaciones).
* Filtrado de registros sin `CustomerID` para evitar sesgos en el perfilamiento.

### 2. Análisis Espectral (Fourier)
Se aplicó la **Transformada Rápida de Fourier (FFT)** sobre la serie temporal diaria de ventas.
* **Resultado:** Detección de un pico armónico dominante en la frecuencia ~0.14.
* **Interpretación:** Confirmación estadística de un ciclo de venta semanal (1/0.14 ≈ 7 días), fundamental para la planificación de inventarios.

### 3. Clustering (K-Means)
Se segmentó la base de clientes utilizando métricas RFM transformadas logarítmicamente para normalizar distribuciones sesgadas.
* 🥇 **Grupo Oro (VIP):** Clientes de alto valor y frecuencia. Estrategia: Fidelización.
* 🥈 **Grupo Plata (Recurrente):** Clientes estables. Estrategia: Cross-selling.
* 🥉 **Grupo Bronce (Ocasional):** Clientes esporádicos. Estrategia: Reactivación.

---

## 📊 Estructura del Dashboard

La aplicación `app.py` cuenta con 4 módulos de navegación:

1.  **🔍 Salud de los Datos:** Diagnóstico técnico y visualización interactiva del espectro de frecuencias (ciclos de venta).
2.  **👥 Perfil de Clientes:** Mapa de dispersión interactivo de los clusters (Oro/Plata/Bronce) con jerarquía visual fija.
3.  **🚀 Tablero de Oportunidades:** KPIs comerciales filtrables por segmento para identificar productos estrella.
4.  **🌍 Análisis Geográfico Global:** Mapa de calor mundial y métricas de dominancia para detectar dependencia de mercados (e.g., UK) y nuevas oportunidades.