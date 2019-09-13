# sdd_deep_learning_test
SDD(surface defect detector) Deep learning test

##Parsytec SDD 장비를 활용하고 있는 유저들 대상으로  딥러닝  환경 구성 방안을 소개 합니다.


작성중


Parsytec SDD에 임베디드 장비(Nvidia jetson TX2)를 연결하여 실시간 작은 이미지 분류 서버를 구성합니다.
임베디드 장비는 TensorRT로 최적화된 모델을 메모리에 로드하여 대기시간을 최소화 합니다.

1. Parsytec SOAP 어플리케이션을 이용한 코일 데이터 인터페이스 환경 구성 
2. status I -> F 일 시  NC 결함을 가공하여 딥러닝 서버로 보낸다.
3. 딥러닝 서버는 이미지를 분류하여 분류한 결과를 테스트 Db에 저장한다. 



참고 자료
socket 
https://github.com/Arsey/keras-transfer-learning-for-oxford102


tensorrt
https://github.com/ardianumam/Tensorflow-TensorRT
https://github.com/NVIDIA-AI-IOT/tf_to_trt_image_classification
