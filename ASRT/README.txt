ASRT V1.1.2 略有修改

Python 3.8.10
pip install numpy matplotlib wave scipy h5py==2.10.0 tensorflow-cpu

from ASRT import asrt
if __name__ == "__main__":
    Stt_local = asrt.SttLocal()
    Stt_local.run("test.wav")

