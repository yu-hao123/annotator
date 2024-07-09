import numpy as np

def retrieve_parity_marks(volume_times_ten : np.ndarray):
    """
    Analyze parity of a volume waveform in order to determine the respiratory
    inspiration and expiration marks.
    This is a particularity of the FlexiMag ventilator.

    Parameters:
    - volume_times_ten: The array that stores all the volume samples multiplied by ten
                        The parity will be analyzed in integer values

    Returns:
    - ins_marks (np.ndarray) : Array conteining the waveform inspiration marks.
    - exp_marks (np.ndarray) : Array conteining the waveform expiration marks.
    """
    ins_marks = []
    exp_marks = []

    v = [int(el) for el in volume_times_ten]

    parity = v[0] % 2
    for i in range(1, len(v)):
        new_parity = v[i] % 2
        if (new_parity != parity and parity == 0):
            ins_marks.append(i)
        elif (new_parity != parity and parity == 1):
            exp_marks.append(i)
        parity = new_parity

    return ins_marks, exp_marks