from django.shortcuts import render,get_object_or_404
from .models import Video
from .forms import VideoForm
import cv2
from .CarmaCam.model._yolo import YoloDetector
from django.conf import settings
from PIL import Image
import json
import os

from celery.result import AsyncResult
from celery import task, current_task, shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from mltr.celery import app


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

@app.task(bind=True)
def do_work(num=100):
    """ Get some rest, asynchronously, and update the state all the time """
    progress_recorder= ProgressRecorder()

    i=0
    while(i<2):
        #sleep(0.1)
        print("do work", i)
        progress_recorder.set_progress(i, 100)
        i+=1
    return 'work complete'

def poll_state(request):
    
    """ A view to report the progress to the user """
    if 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')

    job = AsyncResult(job_id)
    data = {'id': job.id, 'state': job.state, 'info': job.info}

    if data == None:
        return HttpResponse('Invalid job id')        
    return HttpResponse(json.dumps(data), content_type='application/json')

def init_work(request):
    """ A view to start a background job and redirect to the status page """
    job = do_work.delay()
    data = {'id': job.id, 'state': job.state, 'info': job.info}
    return HttpResponse(json.dumps(data), content_type='application/json')


@task
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

def video_yolo_view(request, video_id):
    
    # view that will initialize the processing of video
    # result= process_video.delay(video_id)
    result= do_work.delay()    #this should work and take the video_id as parameter
    context={'task_id': result.task_id}

    return render(request, "video/yolo.html", context=context)


def video_yolo_view(request, video_id):
    obj = get_object_or_404(Video, id=video_id)
    inputfilename = obj.video
    path = settings.MEDIA_ROOT+'/result_json/'+obj.title+'.json'
    if not os.path.isfile(path):
        vidcap = cv2.VideoCapture(settings.MEDIA_ROOT+'/'+str(inputfilename))
        success, image = vidcap.read()
        i = 0
        res={}
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
        print(image.shape)
        detector = YoloDetector((720., 960.))
        print(type(image))
        while success:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            print(type(img))
            im_pil = Image.fromarray(img)
            # out_scores, out_boxes, out_classes, image = detector.detect(im_pil)
            # res[i] = {'out_scores': out_scores.tolist(), 'out_boxes': out_boxes.tolist(),
            #           'out_classes': out_classes.tolist()}
            i+=1
        with open(settings.MEDIA_ROOT+'/result_json/'+obj.title+'.json', 'w') as fp:
            json.dump(res, fp)
    context = {
        "path": path
    }
    return render(request, "video/yolo.html", context)

