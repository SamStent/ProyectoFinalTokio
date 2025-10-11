# 🛒 CompuShop — Dashboard de Métricas Personalizadas

Proyecto de fin de curso en Django.  
Este módulo amplía la aplicación **cuentas** con paneles de control personalizados y métricas dinámicas por usuario.

---

## 🚀 Funcionalidad principal

- Configuración de métricas mediante formulario interactivo (`config_panel`).
- Persistencia en base de datos a través del modelo `ConfiguracionUsuario`.
- Renderizado dinámico de gráficos con **Plotly**.
- Visualización adaptada al rol de usuario (`Gerencia`, `Ventas`, `Almacén`).
- Integración visual con **Bootstrap 5** y mensajes de estado de Django.

---

## ⚙️ Componentes principales

| Módulo | Descripción |
|--------|-------------|
| `models.py` | Modelo `ConfiguracionUsuario` con `JSONField` para métricas activas. |
| `forms.py` | Formulario con checkboxes para elegir métricas visibles. |
| `views_dashboard.py` | Lógica del dashboard dinámico y configuración del panel. |
| `utils/metricas.py` | Cálculos de métricas con Pandas. |
| `utils/graficos.py` | Gráficos interactivos generados con Plotly. |
| `templates/cuentas/dashboard_metricas.html` | Panel visual con cards condicionales. |

---

## 🧠 Flujo de uso

1. Inicia sesión con un usuario del rol **Gerencia** (o Ventas/Almacén).
2. En el panel, pulsa **⚙️ Configurar Panel**.
3. Activa las métricas que quieras visualizar.
4. Guarda los cambios y pulsa **🔄 Actualizar Métricas**.
5. El dashboard mostrará solo los gráficos seleccionados.

---

## 🧩 Requisitos

- Python 3.11+  
- Django 5.2  
- Pandas  
- Plotly  
- Bootstrap 5 (ya integrado en los templates)

Instalación de dependencias:
```bash
pip install django pandas plotly python-decouple
