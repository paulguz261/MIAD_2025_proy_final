import pandas as pd

def create_diff_variables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['fecha'])
    df['delta_volumen'] = df['Volumen'].diff()
    df['delta_presion'] = df['Presion'].diff()
    df['delta_temperatura'] = df['Temperatura'].diff()
    return df