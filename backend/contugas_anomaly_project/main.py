from preprocess import load_and_prepare_data
from model import train_and_predict
from config import INPUT_FILE, OUTPUT_FILE

if __name__ == "__main__":
    print("Cargando y preprocesando datos...")
    df = load_and_prepare_data(INPUT_FILE)

    print("Entrenando modelo y generando etiquetas de anomalía...")
    df = train_and_predict(df)

    print("Guardando resultados en:", OUTPUT_FILE)
    df.to_csv(OUTPUT_FILE, index=False)