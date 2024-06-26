import numpy as np
import cv2
import streamlit as st
from tensorflow import keras
from keras.models import model_from_json
from keras.preprocessing import image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration, WebRtcMode
from tensorflow.keras.preprocessing.image import img_to_array


# load model
emotion_dict = {0:'Raiva', 1:'Nojo', 2:'Medo', 3 :'Feliz', 4: 'Neutro', 5:'Triste', 6: 'Surpresa'}
# load json and create model
json_file = open('modelo/emotion_modelcnn90valAcc.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
classifier = model_from_json(loaded_model_json)

# load weights into new model
classifier.load_weights("modelo/modelo_cnn90valAcc.h5")

#load face
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
except Exception:
    st.write("Error loading cascade classifiers")

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

#load face
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
except Exception:
    st.write("Error loading cascade classifiers")

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class Faceemotion(VideoTransformerBase):
    def __init__(self):
        self.frame_count = 0
        self.faces = []

    def transform(self, frame):
        self.frame_count += 1

        img = frame.to_ndarray(format="bgr24")

        #image gray
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.frame_count % 10 == 0:
            self.faces = face_cascade.detectMultiScale(
                image=img_gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in self.faces:
            cv2.rectangle(img=img, pt1=(x, y), pt2=(
                x + w, y + h), color=(255, 0, 0), thickness=2)

            roi_gray = img_gray[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                prediction = classifier.predict(roi)[0]
                maxindex = int(np.argmax(prediction))
                finalout = emotion_dict[maxindex]
                output = str(finalout)

            label_position = (x, y)
            cv2.putText(img, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return img
    
def main():
    # Face Analysis Application #
    st.title("Reconhecimento de Expressões Faciais em tempo real")
    activities = ["Home", "Reconhecimento de face por Webcam", "Resultados"]
    choice = st.sidebar.selectbox("Escolher atividade", activities)
    st.sidebar.markdown(
        """[Github](https://github.com/ClassNeuralNetwork/Reconhecimento_de_expressoes)""")
    if choice == "Home":

        html_temp_home1 = """<div style="background-color:#6D7B8D;padding:10px">
                                            <h4 style="color:white;text-align:center;">
                                            Aplicativo de Detecção facial e <br>Reconhecimento de Expressões Faciais<br>
                                            Utilizando OpenCV, um modelo CNN próprio e o Streamlit</h4>
                                            </div>
                                            </br>"""
        st.markdown(html_temp_home1, unsafe_allow_html=True)
        st.write("""
                Projeto desenvolvido na disciplina de Redes Neurais - Curso Engenharia de Software - UFERSA (2023.2)
                """)
        

        st.write("""Equipe de Desenvolvimento:
                 
        Anabel Marinho Soares
                
    Nicolas Emanuel Alves Costa
                
    Thiago Luan Moreira Souza""")
                 
    elif choice == "Reconhecimento de face por Webcam":
        st.header("Webcam ao vivo")
        st.write("Clique no START para ativar a detecção de face e reconhecimento de emoções")
        webrtc_streamer(key="example", mode=WebRtcMode.SENDRECV, rtc_configuration=RTC_CONFIGURATION,
                        video_processor_factory=Faceemotion)
        
        st.write("O modelo de reconhecimento de expressões faciais foi treinado com 7 classes de emoções: Raiva, Nojo, Medo, Feliz, Neutro, Triste e Surpresa.")

        st.write("Apesar de não ser 100 por cento preciso, o modelo deve ser capaz de reconhecer a maior parte das expressões que recebe.")

    elif choice == "Resultados":
        st.subheader("Resultados adiquiridos com a rede neural utilizada")
        st.write("""A rede neural foi treinada com 7 classes de emoções: Raiva, Nojo, Medo, Feliz, Neutro, Triste e Surpresa.
                 
        O modelo foi treinado com 28709 imagens e validado com 7178 imagens.
    A acurácia do modelo foi de 90%.
    """)

        st.write("""Equipe de Desenvolvimento:
                 
        Anabel Marinho Soares
                
    Nicolas Emanuel Alves Costa
                
    Thiago Luan Moreira Souza""")
      

    else:
        pass


if __name__ == "__main__":
    main()

