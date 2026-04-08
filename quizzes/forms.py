# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Formlar: Quiz oluşturma/düzenleme, soru ve şık yönetimi
# ----------------------------------------------------------------------

from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Choice


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit_minutes']
        labels = {
            'title': 'Test Adı',
            'description': 'Açıklama',
            'time_limit_minutes': 'Süre Sınırı (dakika)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '180',
                'placeholder': '0 = süresiz'
            }),
        }
        help_texts = {
            'time_limit_minutes': '0 girilirse süre sınırı uygulanmaz. Maksimum 180 dakika.',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'order']
        labels = {'text': 'Soru Metni', 'order': 'Sıra'}
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        labels = {'text': 'Şık Metni', 'is_correct': 'Doğru Cevap'}
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=4,
    max_num=6,
    can_delete=True
)
