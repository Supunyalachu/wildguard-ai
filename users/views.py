from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from ultralytics import YOLO
from .models import Detection, Alert
from django.contrib.auth import get_user_model
from django.http import HttpResponse

MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    'models',
    'animal_detector_v1.pt'
)

model = YOLO(MODEL_PATH)

def home(request):
    return render(request, 'users/home.html')
def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        else:

            return render(
                request,
                'users/login.html',
                {'error': 'Invalid username or password.'}
            )

    return render(request, 'users/login.html')


def signup(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:

            return render(
                request,
                'users/signup.html',
                {'error': 'Passwords do not match.'}
            )

        if User.objects.filter(username=username).exists():

            return render(
                request,
                'users/signup.html',
                {'error': 'Username already exists.'}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('dashboard')

    return render(request, 'users/signup.html')

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

def logout_view(request):

    logout(request)

    return redirect('home')
def detect_animal(request):
    return render(request, 'users/detect.html')



@login_required
def history(request):
    detections = Detection.objects.all().order_by('-detected_at')

    return render(
        request,
        'users/history.html',
        {'detections': detections}
    )
@csrf_exempt
@require_POST
def detect_api(request):

    image = request.FILES.get('image')

    if not image:
        return JsonResponse({
            'success': False,
            'error': 'No image uploaded.'
        }, status=400)

    try:
        img = Image.open(image).convert('RGB')

        results = model(
            img,
            conf=0.45,
            verbose=False
        )

        detections = []

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                animal = result.names[class_id]

                detection = Detection.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    animal=animal,
                    confidence=confidence * 100
                )
                alert = Alert.objects.create(
                    detection=detection,
                    user=request.user if request.user.is_authenticated else None,
                    message=f"🚨 {animal} detected with {confidence * 100:.2f}% confidence."
                )
                recipients = list(
                    User.objects
                    .exclude(email='')
                    .values_list('email', flat=True)
)

                send_mail(
                    subject=f"🚨 WildGuard AI Alert: {animal} Detected",
                    message=(
                        f"WildGuard AI has detected an animal.\n\n"
                        f"Animal: {animal}\n"
                        f"Confidence: {confidence * 100:.2f}%\n"
                        f"Detection ID: {detection.id}\n"
                    ),
                    from_email=None,
                    recipient_list=recipients,
                )

                alert.sent = True
                alert.save()   

                detections.append({
                    'animal': animal,
                    'confidence': round(confidence * 100, 2),
                    'id': detection.id
                })

        if not detections:
            return JsonResponse({
                'success': True,
                'detected': False,
                'message': 'No animal detected.',
                'detections': []
            })

        return JsonResponse({
            'success': True,
            'detected': True,
            'detections': detections
        })

    except Exception as e:

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
def test_email(request):
    send_mail(
        subject='WildGuard AI Test Alert',
        message='This is a test email from the WildGuard AI Django backend.',
        from_email=None,
        recipient_list=[settings.WILDGUARD_ALERT_EMAIL],
    )

    return JsonResponse({
        'success': True,
        'message': 'Test email sent.'
    }) 

def create_admin(request):
    User = get_user_model()

    username = "admin"
    password = "Admin@12345"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email="admin@wildguard.com",
            password=password
        )
        return HttpResponse("Admin created successfully")

    return HttpResponse("Admin already exists")