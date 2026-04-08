#!/bin/bash
# EduPlatform Kurulum ve Çalıştırma Scripti

echo "🎓 EduPlatform Kurulumu Başlatılıyor..."
echo "========================================"

# 1. Sanal ortam oluştur
echo "📦 Sanal ortam oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate

# 2. Bağımlılıkları yükle
echo "📥 Bağımlılıklar yükleniyor..."
pip install -r requirements.txt

# 3. Veritabanı migration
echo "🗄️  Veritabanı oluşturuluyor..."
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations quizzes
python manage.py migrate

# 4. Demo veriler oluştur
echo "👤 Demo kullanıcılar oluşturuluyor..."
python manage.py shell << 'PYTHON_EOF'
from users.models import User
from courses.models import Course, Lesson, Enrollment
from quizzes.models import Quiz, Question, Choice

# Öğretmen oluştur
if not User.objects.filter(username='ogretmen').exists():
    teacher = User.objects.create_user(
        username='ogretmen',
        password='sifre123',
        first_name='Ahmet',
        last_name='Yılmaz',
        email='ogretmen@edu.com',
        role='teacher',
        bio='Matematik ve Fen Bilimleri öğretmeni. 10 yıllık deneyim.'
    )
    print(f"✅ Öğretmen oluşturuldu: {teacher.username} / şifre: sifre123")

    # Öğrenci oluştur
    student = User.objects.create_user(
        username='ogrenci',
        password='sifre123',
        first_name='Elif',
        last_name='Kaya',
        email='ogrenci@edu.com',
        role='student',
        bio='9. sınıf öğrencisi.'
    )
    print(f"✅ Öğrenci oluşturuldu: {student.username} / şifre: sifre123")

    # Ders oluştur
    course = Course.objects.create(
        teacher=teacher,
        title='Python Programlamaya Giriş',
        description='Sıfırdan Python öğrenin. Değişkenler, döngüler, fonksiyonlar ve daha fazlası.'
    )

    # Konular ekle
    Lesson.objects.create(course=course, title='Python Nedir?', order=1,
        content='Python, 1991 yılında Guido van Rossum tarafından geliştirilen yüksek seviyeli, genel amaçlı bir programlama dilidir.\n\nPython\'un özellikleri:\n• Okunması ve yazması kolay sözdizimi\n• Geniş standart kütüphane\n• Platform bağımsız çalışma\n• Nesne yönelimli programlama desteği')
    Lesson.objects.create(course=course, title='Değişkenler ve Veri Tipleri', order=2,
        content='Python\'da değişkenler dinamik olarak tiplendirilir.\n\nTemel veri tipleri:\n• int: Tam sayılar (örn: 42)\n• float: Ondalıklı sayılar (örn: 3.14)\n• str: Metin (örn: "Merhaba")\n• bool: Mantıksal (True / False)\n• list: Liste ([1, 2, 3])\n• dict: Sözlük ({"anahtar": "değer"})')
    Lesson.objects.create(course=course, title='Koşullar ve Döngüler', order=3,
        content='if-elif-else yapısı:\n\nif x > 0:\n    print("Pozitif")\nelif x < 0:\n    print("Negatif")\nelse:\n    print("Sıfır")\n\nfor döngüsü:\nfor i in range(5):\n    print(i)\n\nwhile döngüsü:\nwhile x > 0:\n    x -= 1')

    # Quiz oluştur
    quiz = Quiz.objects.create(
        course=course,
        title='Python Temelleri Quiz',
        description='Python\'un temel kavramlarını test edin.'
    )
    q1 = Question.objects.create(quiz=quiz, text='Python hangi yılda geliştirilmiştir?', order=1)
    Choice.objects.create(question=q1, text='1985', is_correct=False)
    Choice.objects.create(question=q1, text='1991', is_correct=True)
    Choice.objects.create(question=q1, text='2000', is_correct=False)
    Choice.objects.create(question=q1, text='2010', is_correct=False)

    q2 = Question.objects.create(quiz=quiz, text='Aşağıdakilerden hangisi Python\'da tam sayı (int) örneğidir?', order=2)
    Choice.objects.create(question=q2, text='"42"', is_correct=False)
    Choice.objects.create(question=q2, text='42.0', is_correct=False)
    Choice.objects.create(question=q2, text='42', is_correct=True)
    Choice.objects.create(question=q2, text='True', is_correct=False)

    q3 = Question.objects.create(quiz=quiz, text='Python\'da yorum satırı hangi karakterle başlar?', order=3)
    Choice.objects.create(question=q3, text='//', is_correct=False)
    Choice.objects.create(question=q3, text='--', is_correct=False)
    Choice.objects.create(question=q3, text='/*', is_correct=False)
    Choice.objects.create(question=q3, text='#', is_correct=True)

    # Öğrenciyi derse kaydet
    Enrollment.objects.create(student=student, course=course)
    print(f"✅ Demo ders ve içerikler oluşturuldu: {course.title}")
else:
    print("ℹ️  Demo veriler zaten mevcut.")
PYTHON_EOF

# 5. Süper kullanıcı oluştur (isteğe bağlı)
echo ""
echo "👑 Admin paneli için süper kullanıcı oluşturmak ister misiniz?"
echo "   (Boş bırakmak için Enter'a basın)"
read -p "   Kullanıcı adı [admin]: " admin_user
admin_user=${admin_user:-admin}

if [ ! -z "$admin_user" ]; then
    python manage.py shell -c "
from users.models import User
if not User.objects.filter(username='$admin_user').exists():
    User.objects.create_superuser('$admin_user', 'admin@edu.com', 'admin123', role='teacher')
    print('✅ Süper kullanıcı oluşturuldu: $admin_user / admin123')
else:
    print('ℹ️  $admin_user zaten mevcut.')
"
fi

echo ""
echo "========================================"
echo "🚀 EduPlatform hazır!"
echo ""
echo "📌 Demo Hesaplar:"
echo "   Öğretmen: ogretmen / sifre123"
echo "   Öğrenci:  ogrenci  / sifre123"
echo "   Admin:    $admin_user / admin123"
echo ""
echo "🌐 Sunucuyu başlatmak için:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "   Tarayıcıda açın: http://127.0.0.1:8000"
echo "   Admin panel:     http://127.0.0.1:8000/admin"
echo "========================================"

# 6. Sunucuyu başlat
read -p "Sunucu şimdi başlatılsın mı? (e/h): " start_server
if [ "$start_server" = "e" ] || [ "$start_server" = "E" ]; then
    python manage.py runserver
fi
