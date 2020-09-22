from flask import *
# from flask import Flask, render_template, Response, request
# emulated camera
import cv2, numpy as np
from threading import Thread
from darknet import darknet
 
#1. 사용할 변수 선언
config_path = "D:/python_module/darknet-master/build\darknet/x64/project/myyolov3.cfg"
weigh_path = "D:/python_module/darknet-master/build/darknet/x64/project/backup/myyolov3_final.weights"
meta_path = "D:/python_module/darknet-master/build\darknet/x64/project/my.data"
video_path = "D:/python_module/darknet-master/build\darknet/x64/project/22-2.mp4"
threshold = 0.25

video1 = "D:/python_module/darknet-master/build\darknet/x64/project/22-2.mp4"
video2 = "D:/python_module/darknet-master/build\darknet/x64/project/26-4.mp4"

#2. 관련 파일 load
# cfg(모델관련)와 weight 파일 아스키코드로 load
net = darknet.load_net(bytes(config_path, "ascii"), bytes(weigh_path, "ascii"), 0) 
# data(classes, train, valid, names, backup의 경로가 명시된 텍스트파일)  아스키코드로 load
meta = darknet.load_meta(bytes(meta_path, "ascii"))
# 비디오의 프레임을 추출하는 VideoCapture 함수
cap = cv2.VideoCapture(video_path)
 
#3. WebcamVideoStream : camera를 thread 이용해서 열어준다
class WebcamVideoStream:
        # camera 시작
       def __init__(self, src=0):
           print("init")
           self.stream = cv2.VideoCapture(src)
           (self.grabbed, self.frame) = self.stream.read()
 
           self.stopped = False

        # thread를 이용해서 시작
       def start(self):
           print("start thread")
           t = Thread(target=self.update, args=())
           # daemon 쓰레드란 백그라운드에서 실행되는 쓰레드. 메인쓰레드가 종료되면 즉시 종료
           t.daemon = True
           t.start()
           return self

        # 프레임 업데이트
       def update(self):
           print("read")
           while True:
               if self.stopped:
                   return
 
               (self.grabbed, self.frame) = self.stream.read()
 
       def read(self):
           return self.frame
 
       def stop(self):
           self.stopped = True


def gen(camera):
        # """Video streaming generator function."""
    i = 0    
    while True:
        i += 1
        image = camera.read()
        image = cv2.resize(image, dsize=(640, 480), interpolation=cv2.INTER_AREA)
        print(i)
        # if not ret: 
            # break 
        frame = darknet.nparray_to_image(image)
        r = darknet.detect_image(net, meta, frame, thresh=.5, hier_thresh=.5, nms=.45, debug= False)
        print(r)
        boxes = [] 

        for k in range(len(r)): 
            width = r[k][2][2] 
            height = r[k][2][3] 
            center_x = r[k][2][0] 
            center_y = r[k][2][1] 
            bottomLeft_x = center_x - (width / 2) 
            bottomLeft_y = center_y - (height / 2) 
            x, y, w, h = bottomLeft_x, bottomLeft_y, width, height
            mytexts = r[k][0]
            mythresh = r[k][1] 
            boxes.append((x, y, w, h, mytexts, mythresh))
        print(1)



        for k in range(len(boxes)): 
            x, y, w, h, texts, threshs = boxes[k] 
            top = max(0, np.floor(x + 0.5).astype(int)) 
            left = max(0, np.floor(y + 0.5).astype(int)) 
            right = min(image.shape[1], np.floor(x + w + 0.5).astype(int)) 
            bottom = min(image.shape[0], np.floor(y + h + 0.5).astype(int)) 
            # cv2.rectangle(image, (top, left), (right, bottom), (0, 255, 0), 1)
            
            if texts.decode('utf-8') == 'normal':
                cv2.rectangle(image, (top, left), (right, bottom), (255, 0, 0), 2)
                cv2.putText(image, texts.decode('utf-8') + '('+ str(threshs*100)[:5] + '%)', (top, left-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))
            
            elif texts.decode('utf-8') == 'fighting':
                cv2.rectangle(image, (top, left), (right, bottom), (0, 0, 255), 2)
                cv2.putText(image, texts.decode('utf-8') + '('+ str(threshs*100)[:5] + '%)', (top, left-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        ret, jpeg = cv2.imencode('.jpg', image)
        darknet.free_image(frame) ## darknet에서 쓰는 c언어 동적할당 해제해주는 함수(써주어야 메모리가 버틴다.)

        if jpeg is not None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        else:
            print("frame is none")

 
video = [(1,video1), (2,video2)]
app = Flask(__name__)


@app.route('/')
def login_form():

    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
    rows = video
    if request.method == 'POST':

        if(request.form['id'] == 'admin' and request.form['pw'] == 'admin123'):

            session['logged'] = True

            session['user'] = request.form['id']

            return render_template('camera_index.html', rows = rows)

        else:

            return """<script>alert("wrong!");location.href='/';</script>"""

    else:

        return """<script>alert("not allowd!");location.href='/';</script>"""

app.secret_key = 'sample_secret'




@app.route('/index')
def index():
    # http://192.168.0.120:5000/index?id=2
    # request.args는 url 파라미터 값을 키=값 쌍으로 가지고 있는 딕셔너리 형태
    ids = request.args.get('id')
    print(ids)
    rows = video
    return render_template('camera.html', rows=[rows[int(ids)-1]])
 
@app.route('/index/video_feed')
def video_feed():
        ids = request.args.get('id')
        print(ids)
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen(WebcamVideoStream(src=video[int(ids)-1][1]).start()),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
 

if __name__ == '__main__':
       app.run(host='127.0.0.1', debug=True, threaded=True)