import pandas as pd
import os

# 1. Configuración de ruta y archivo
ruta = r'C:\Users\UsuarioM\Desktop\HACKATON'
os.chdir(ruta)
nombre_excel = 'Datasets.xlsx'

try:
    # 2. Carga de datos
    df_v = pd.read_excel(nombre_excel, sheet_name='Ventas')
    df_p = pd.read_excel(nombre_excel, sheet_name='Potencial')
    
    # Asegurar formato de fecha
    df_v['Fecha'] = pd.to_datetime(df_v['Fecha'])
    df_v['Mes'] = df_v['Fecha'].dt.to_period('M')

    # 3. Cálculo de Media Histórica por Cliente
    # Calculamos cuánto suele comprar cada cliente al mes
    ventas_cliente_mes = df_v.groupby(['Id. Cliente', 'Mes'])['Valores_H'].sum().reset_index()
    media_cliente = ventas_cliente_mes.groupby('Id. Cliente')['Valores_H'].mean().reset_index()
    media_cliente.columns = ['Id. Cliente', 'Media_Mensual_Historica']

    # 4. Cálculo de Facturación Real (Último Mes)
    ultimo_mes = df_v['Mes'].max()
    ventas_ultimo_mes = ventas_cliente_mes[ventas_cliente_mes['Mes'] == ultimo_mes]
    
    # 5. Cruce de datos para detectar bajadas
    historial = pd.merge(media_cliente, ventas_ultimo_mes[['Id. Cliente', 'Valores_H']], on='Id. Cliente', how='left')
    historial['Valores_H'] = historial['Valores_H'].fillna(0) # Si no compró, es 0
    historial['Variacion_vs_Media'] = historial['Valores_H'] - historial['Media_Mensual_Historica']
    historial['%_Cambio'] = (historial['Variacion_vs_Media'] / historial['Media_Mensual_Historica']) * 100

    # 6. Alertas: Filtrar clientes con caída significativa (>20% por debajo de su media)
    alertas_clientes = historial[historial['%_Cambio'] <= -20].sort_values(by='%_Cambio')

    # 7. RESULTADOS
    print(f"--- ANÁLISIS DE HISTORIAL (Mes actual: {ultimo_mes}) ---")
    print(f"Total clientes analizados: {len(historial)}")
    print(f"Clientes en estado de ALERTA (caída >20%): {len(alertas_clientes)}")
    print("\nTOP 10 CLIENTES CON MAYOR CAÍDA:")
    print(alertas_clientes[['Id. Cliente', 'Media_Mensual_Historica', 'Valores_H', '%_Cambio']].head(10))

    # Guardar a Excel para que lo revises
    alertas_clientes.to_excel('Alertas_Clientes_Detalle.xlsx', index=False)
    print("\n✅ Se ha generado el archivo 'Alertas_Clientes_Detalle.xlsx' con el historial completo.")

except Exception as e:
    print(f"❌ Error: {e}")