# Optimizador de Carga EV · PVPC

App web para calcular las horas más baratas de carga de vehículo eléctrico según tarifas PVPC.

## Cómo funciona

- **GitHub Actions** descarga los precios PVPC automáticamente cada día a las 20:45h y 21:15h (hora España) y los guarda en `data/prices.json`
- La web lee ese JSON estático — sin problemas de CORS ni APIs externas
- Velocidad de carga configurada: 6%/h · 7,4 kW

## Primera vez: obtener precios manualmente

1. Ve a la pestaña **Actions** en tu repositorio
2. Selecciona el workflow **"Actualizar precios PVPC"**
3. Pulsa **"Run workflow"** → **"Run workflow"**
4. Espera ~30 segundos y recarga la web

A partir de ahí se actualizará solo cada noche.

## Fuente de datos

[api.preciodelaluz.org](https://api.preciodelaluz.org) · Tarifa regulada PVPC 2.0TD · Red Eléctrica de España
