import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_dataset(file):
    import pandas as pd

    xl = pd.ExcelFile(file)
    dataset = {}

    for nome in xl.sheet_names:
        folha = pd.read_excel(xl, sheet_name=nome).copy()

        partes = nome.split("_")

        # valida nome da sheet
        if len(partes) < 2:
            print(f"Sheet inválida: {nome}")
            continue

        data = partes[0]
        conc = partes[1]

        # encontrar colunas relevantes
        indices = [i for i, col in enumerate(folha.columns)
                   if "gray value" in str(col).lower()]

        # validar estrutura mínima
        if len(indices) < 2:
            print(f"Sheet ignorada (sem brutos/gvr completo): {nome}")
            continue

        inicio_brutos = indices[0]
        inicio_gvr = indices[1]

        brutos = folha.iloc[:, inicio_brutos:inicio_gvr].copy()
        gvr = folha.iloc[:, inicio_gvr:].copy()

        brutos = brutos.dropna(axis=1, how="all")
        gvr = gvr.dropna(axis=1, how="all")

        brutos = brutos.rename(columns={brutos.columns[0]: "Time(hrs)"})
        gvr = gvr.rename(columns={gvr.columns[0]: "Time(hrs)"})

        if data not in dataset:
            dataset[data] = {}

        dataset[data][conc] = {
            "brutos": brutos,
            "gvr": gvr
        }

    return dataset


def clean_Nas(dataset):
    """
    Removes rows containing NaN values in experimental data columns.

    Keeps only rows where at least one valid value exists
    (excluding the time column).

    Parameters
    ----------
    dataset : dict
        Dictionary containing structured experimental data.

    Returns
    -------
    dict
        Cleaned dataset with fully invalid rows removed.
    """
    
    for data, concs in dataset.items():
        for conc, datasets in concs.items():
            brutos = datasets["brutos"]
            gvr    = datasets["gvr"]
            dataset[data][conc]["brutos"] = brutos[brutos.iloc[:, 0:].notna().all(axis=1)].reset_index(drop=True)
            dataset[data][conc]["gvr"]    = gvr[gvr.iloc[:, 0:].notna().all(axis=1)].reset_index(drop=True)

    return dataset


def get_std(df, output):
    """
    Calculates the standard deviation over time and detects the first moment
    at which it exceeds the threshold of 0.05.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing time and measurement columns.
    output : str
        If set to "std", prints initial and final standard deviation values.

    Returns
    -------
    float or None
        Time at which the standard deviation first exceeds 0.05.
    """
    t = 0
    tempo_threshold = None  #saves the time
    for i in range(len(df)):
        std = np.std(df.iloc[i, 1:])
        if std > 0.05 and t == 0:
            tempo_threshold = df.iloc[i, 0]  #saves the time
            t = 1
        if output == "std":
            if i == 0:
                print(f"std inicial: {std:.4f}")
            if i == len(df) - 1:
                print(f"std final: {std:.4f}")
            
    return tempo_threshold  


def get_fig_std(data, conc, df, tipo_dados, time):
    """
    Generates a time-series plot of measurements and optionally marks a critical time point.

    Parameters
    ----------
    data : str
        Experiment date identifier.
    conc : str
        Concentration associated with the data.
    df : pandas.DataFrame
        DataFrame containing time and measurement columns.
    tipo_dados : str
        Type of data (e.g. raw, processed).
    time : float or None
        Time at which the standard deviation exceeds the threshold.
    """

    fig, ax = plt.subplots(figsize=(12, 4))
        
    for col in df.columns[1:]:
        ax.plot(df["Time(hrs)"], df[col], label=col)

    if time is not None:
        ax.axvline(x=time, color="red", linestyle="-", label=f"std > 0.05 (t={time:.2f})")
        
    ax.set_title(f"{data} - {conc} - {tipo_dados}")
    ax.set_xlabel("Time (hrs)")
    ax.set_ylabel(tipo_dados)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()