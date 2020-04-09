from django.shortcuts import render,get_object_or_404
from .models import Video
from .forms import VideoForm
import cv2
#from CarmaCam.model._yolo import YoloDetector
from django.conf import settings
from PIL import Image
import json
import os

import threading
import time
from django.http import JsonResponse


# Create your views here.
def  video_detail_view(request, video_id):
    obj = get_object_or_404(Video, id=video_id)
    context = {
        "object": obj
    }
    return render(request, "video/detail.html", context)


def video_update_view(request, video_id):
    obj = get_object_or_404(Video, id=video_id)
    form = VideoForm(request.POST or None, request.FILES or None,instance=obj)
    if form.is_valid():
        form.save()
    context = {
        "form":form
    }
    return render(request, "video/create.html", context)


def video_create_view(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        uploaded_file = request.FILES
        if form.is_valid():
            form.save()

            # model_instance.name = uploaded_file['image'].name
            # model_instance.save()
    else:
        form = VideoForm()
    context = {
        "form":form
    }

    return render(request, "video/create.html", context)


def video_list_view(request):
    queryset = Video.objects.all()
    context = {
        "object_list": queryset
    }
    return render(request, "video/show.html", context)


def process_video(video_id):

    obj = get_object_or_404(Video, id=video_id)
    inputfilename = obj.video
    path = settings.MEDIA_ROOT+'/result_json/'+obj.title+'.json'
    
    if not os.path.isfile(path):
        vidcap = cv2.VideoCapture(settings.MEDIA_ROOT+'/'+str(inputfilename))
        success, image = vidcap.read()
        i = 1
        # get total no of frames to check how many frames processed 
        total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

        res={}
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
        print(image.shape)
        detector = YoloDetector((720., 960.))
        print(type(image))
        while success:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            print(type(img))
            im_pil = Image.fromarray(img)


            current_task.update_state(state='PROGRESS',
            meta={'current': i, 'total': total_frames})

            # out_scores, out_boxes, out_classes, image = detector.detect(im_pil)
            # res[i] = {'out_scores': out_scores.tolist(), 'out_boxes': out_boxes.tolist(),
            #           'out_classes': out_classes.tolist()}
            i+=1
        with open(settings.MEDIA_ROOT+'/result_json/'+obj.title+'.json', 'w') as fp:
            json.dump(res, fp)
    
    result = {
        "path": path
    }

    return result

def yolo_task(lk, id):
     
    lk.acquire()
    logging.info("Thread received %s", id)
    
    for i in range(0,10):
        pass

    task = ThreadTask.objects.get(pk=id)
    task.is_done = True
    task.save()
    logging.info("Thread finish task %s", id)

    lk.release()

    return

def startThreadTask(request, id):

    lock = 1
    t = threading.Thread(target=yolo_task, args=[lock, id])
    t.setDaemon(True)
    t.start()
    
    return JsonResponse({'id':id})

i=0
def checkThreadTask(request,task_id):
    
    global i
    #task = ThreadTask.objects.get(pk=task_id)
    #isdone= task.is_done
    isdone= False;
    i+= 1
    if (i>=10):
        isdone= True;

    return JsonResponse({'task_done': isdone})

### yolo part ###
def video_yolo_view(request, video_id):
    obj = get_object_or_404(Video, id=video_id)

    id=video_id
    inputfilename = obj.video
    path = settings.MEDIA_ROOT+'/result_json/'+obj.title+'.json'

    startThreadTask(request, id)
    context=  {'task_id': id}
    return render(request, "video/yolo.html", context)

